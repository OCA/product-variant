# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.addons.decimal_precision as dp
from odoo import _, api, models, fields


class StockTransferManageVariant(models.TransientModel):
    _name = 'stock.transfer.manage.variant'

    def _default_variant_line_ids(self):
        context = self.env.context
        picking = self.env['stock.picking'].browse(context['active_id'])
        pack_ops = picking.pack_operation_ids.filtered(
            lambda x: len(
                x.product_id.product_tmpl_id.attribute_line_ids
            ) < 2
        )
        if not pack_ops:  # pragma: no cover
            return False
        has_single_variant = bool(pack_ops.filtered(
            lambda x: not x.product_id.attribute_line_ids
        ))
        columns = [
            x for x in pack_ops.mapped('product_id.attribute_value_ids')
        ]
        if has_single_variant:
            columns.append(False)
        rows = pack_ops.mapped('product_id.product_tmpl_id')
        lines = []
        for product_tmpl in rows:
            for value in columns:
                # Filter the corresponding product for that value
                if not value:
                    variants = product_tmpl.product_variant_ids
                    prod = variants[0] if len(variants) == 1 else False
                else:
                    prod = product_tmpl.product_variant_ids.filtered(
                        lambda x: not(value - x.attribute_value_ids)
                    )[:1]
                pack_op = pack_ops.filtered(lambda x: x.product_id == prod)[:1]
                # We add plain char fields because web client doesn't resolve
                # correctly the name_get of the many2one fields
                lines.append((0, 0, {
                    'product_id': prod.id if prod else False,
                    'disabled': not bool(prod),
                    'value_x': value,
                    'value_x_label': (
                        _('N/D') if not value else value.name_get()[0][1]
                    ),
                    'value_y': product_tmpl,
                    'value_y_label': product_tmpl.name_get()[0][1],
                    'qty_done': pack_op.qty_done,
                }))
        return lines

    variant_line_ids = fields.Many2many(
        comodel_name='stock.transfer.manage.variant.line', string="Lines",
        default=_default_variant_line_ids,
        relation="stock_transfer_manage_variant_line_rel",
    )

    @api.multi
    def button_transfer_to_picking(self):
        context = self.env.context
        picking = self.env['stock.picking'].browse(context['active_id'])
        for line in self.variant_line_ids.filtered('product_id'):
            pack_op = picking.pack_operation_ids.filtered(
                lambda x: x.product_id == line.product_id
            )
            pack_op.qty_done = line.qty_done


class StockTransferManageVariantLine(models.TransientModel):
    _name = 'stock.transfer.manage.variant.line'

    product_id = fields.Many2one(
        comodel_name='product.product', string="Variant", readonly=True,
    )
    disabled = fields.Boolean()
    value_x = fields.Many2one(comodel_name='product.attribute.value')
    value_x_label = fields.Char()
    value_y = fields.Many2one(comodel_name='product.template')
    value_y_label = fields.Char()
    qty_done = fields.Float(
        string="Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
    )
