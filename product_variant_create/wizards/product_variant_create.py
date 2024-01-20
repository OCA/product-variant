#  -*- coding: utf-8 -*-
#  Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models, Command
from odoo.exceptions import UserError
from odoo.tools import groupby

_logger = logging.getLogger(__name__)


def _ids2str(ids):
    return ','.join([str(i) for i in sorted(ids)])


class ProductVariantCreate(models.TransientModel):
    _name = 'product.variant.create'
    _inherit = ['image.mixin']
    _description = 'Create Variant from attribute'

    @api.model
    def default_get(self, default_fields):
        result = super().default_get(default_fields)
        if not result.get('product_tmpl_id') and self._context.get('active_model') == 'product.template':
            product_tmpl_id = self.env['product.template'].browse(self._context['active_id'])
            product_template_attribute_value_ids = self.env['product.template.attribute.value'].search(
                [('product_tmpl_id', '=', product_tmpl_id.id)],
            )
            attribute_ids = []
            for attribute, values in groupby(
                product_template_attribute_value_ids.sorted(lambda r: r.attribute_id.id),
                lambda r: r.attribute_id
            ):
                # _logger.info(f'{attribute}::{list(values)}')
                attribute_ids.append(Command.create({
                    'product_tmpl_id': product_tmpl_id.id,
                    # 'attribute_line_id': values[0].attribute_line_id.id,
                    'attribute_id': attribute.id,
                }))
            if not attribute_ids:
                UserError(_('In template is not defined any attribute, maybe is single product'))
            result.update(
                product_template_attribute_value_ids=attribute_ids,
                product_tmpl_id=product_tmpl_id.id,
            )
        return result

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template'
    )
    product_template_attribute_value_ids = fields.One2many(
        comodel_name='product.variant.create.lines',
        inverse_name='product_variant_create_id',
        string='Product attributes',
    )
    combination_indices = fields.Char()
    default_code = fields.Char('Internal Reference')
    barcode = fields.Char(
        'Barcode',
        help="International Article Number used for product identification."
    )
    volume = fields.Float('Volume', digits='Volume')
    weight = fields.Float('Weight', digits='Stock Weight')

    @api.onchange('combination_indices')
    def _onchange_combination_indices(self):
        self.ensure_one()
        if self.combination_indices:
            product_id = self.env['product.product'].search([
                ('product_tmpl_id', '=', self.product_tmpl_id.id),
                ('combination_indices', '=', self.combination_indices)
            ])
            if product_id:
                raise UserError(_("This product is available"))

    def process(self):
        self.ensure_one()
        if self.product_tmpl_id:
            attribute_value_ids = []
            product_attribute_value_ids = self.product_template_attribute_value_ids.mapped('product_attribute_value_id')
            self.combination_indices = _ids2str(product_attribute_value_ids.ids)
            # _logger.info(f"{self.product_template_attribute_value_ids.mapped('product_attribute_value_id').ids}::{self.combination_indices}")
            if self.combination_indices:
                for attribute_line_ids in self.product_tmpl_id.attribute_line_ids:
                    attribute_id = self.product_template_attribute_value_ids. \
                        filtered(lambda r: r.attribute_id.id == attribute_line_ids.attribute_id.id)
                    if attribute_id.product_attribute_value_id.id not in attribute_line_ids.value_ids.ids:
                        attribute_line_ids.write({
                            'value_ids':
                                [Command.set(attribute_line_ids.mapped('value_ids').ids
                                             + attribute_id.product_attribute_value_id.ids)]
                        })
                    product_template_attribute_value_id = self.env['product.template.attribute.value'].search([
                            ('product_attribute_value_id', '=', attribute_id.product_attribute_value_id.id),
                            ('attribute_id', '=', attribute_id.attribute_id.id),
                            ('product_tmpl_id', '=', self.product_tmpl_id.id)
                        ])
                    if product_template_attribute_value_id:
                        attribute_value_ids.append(product_template_attribute_value_id.id)
                    # _logger.info(f"{attribute_id.product_attribute_value_id} in {attribute_line_ids.value_ids}:::{product_template_attribute_value_id}")

                if attribute_value_ids:
                    self.sudo().product_tmpl_id.write({
                        'product_variant_ids': [Command.create({
                            'active': True,
                            'product_tmpl_id': self.product_tmpl_id.id,
                            'default_code': self.default_code,
                            'barcode': self.barcode,
                            'volume': self.volume,
                            'weight': self.weight,
                            'image_1920': self.image_1920,
                            'product_template_attribute_value_ids': [Command.set(attribute_value_ids)]  # product.template.attribute.value
                        })]
                    })


class ProductVariantCreateLines(models.TransientModel):
    _name = 'product.variant.create.lines'
    _description = 'Create Variant from attribute lines'

    product_variant_create_id = fields.Many2one('product.variant.create', string='Product variant create')
    product_tmpl_id = fields.Many2one(
            'product.template',
            string='Product Template',
        )
    product_attribute_value_id = fields.Many2one(
        'product.attribute.value', string='Attribute Value',
        required=True)
    attribute_id = fields.Many2one('product.attribute', string="Attribute")
