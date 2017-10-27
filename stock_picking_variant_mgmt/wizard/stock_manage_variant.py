# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.addons.decimal_precision as dp
from odoo import api, models, fields


class StockManageVariant(models.TransientModel):
    _name = 'stock.manage.variant'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string="Template", required=True,
    )
    variant_line_ids = fields.Many2many(
        comodel_name='stock.manage.variant.line', string="Variant Lines",
    )

    # HACK: https://github.com/OCA/server-tools/pull/492#issuecomment-237594285
    @api.multi
    def onchange(self, values, field_name, field_onchange):  # pragma: no cover
        if "variant_line_ids" in field_onchange:
            for sub in ("product_id", "disabled", "value_x", "value_y",
                        "product_uom_qty"):
                field_onchange.setdefault("variant_line_ids." + sub, u"")
        return super(StockManageVariant, self).onchange(
            values, field_name, field_onchange)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.variant_line_ids = [(6, 0, [])]
        template = self.product_tmpl_id
        context = self.env.context
        record = self.env[context['active_model']].browse(
            context['active_id'],
        )
        if context['active_model'] == 'stock.move':
            picking = record.picking_id
        else:
            picking = record
        num_attrs = len(template.attribute_line_ids)
        if not template or not num_attrs:  # pragma: no cover
            return
        line_x = template.attribute_line_ids[0]
        line_y = False if num_attrs == 1 else template.attribute_line_ids[1]
        lines = []
        for value_x in line_x.value_ids:
            for value_y in line_y and line_y.value_ids or [False]:
                # Filter the corresponding product for that values
                values = value_x
                if value_y:  # pragma: no cover
                    values += value_y
                product = template.product_variant_ids.filtered(
                    lambda x: not(values - x.attribute_value_ids)
                )[:1]
                move = picking.move_lines.filtered(
                    lambda x: x.product_id == product
                )[:1]
                lines.append((0, 0, {
                    'product_id': product,
                    'disabled': not bool(product),
                    'value_x': value_x,
                    'value_y': value_y,
                    'product_uom_qty': move.product_uom_qty,
                }))
        self.variant_line_ids = lines

    @api.multi
    def button_transfer_to_picking(self):
        context = self.env.context
        record = self.env[context['active_model']].browse(
            context['active_id'],
        )
        if context['active_model'] == 'stock.move':
            picking = record.picking_id
        else:
            picking = record
        Move = self.env['stock.move']
        moves2unlink = Move
        for line in self.variant_line_ids:
            move = picking.move_lines.filtered(
                lambda x: x.product_id == line.product_id
            )
            if move:
                if not line.product_uom_qty:
                    # Done this way because there's a side effect removing here
                    moves2unlink |= move
                else:
                    move.product_uom_qty = line.product_uom_qty
                    move.do_unreserve()
                    move.action_assign()
            elif line.product_uom_qty:
                move = Move.new({
                    'product_id': line.product_id.id,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                })
                move.onchange_product_id()
                move.product_uom_qty = line.product_uom_qty
                Move.create(move._convert_to_write(move._cache))
        # With this we assure integrity
        if picking.state != 'draft':  # pragma: no cover
            picking.do_prepare_partial()
        moves2unlink.unlink()


class StockManageVariantLine(models.TransientModel):
    _name = 'stock.manage.variant.line'

    product_id = fields.Many2one(
        comodel_name='product.product', string="Variant", readonly=True,
    )
    disabled = fields.Boolean()
    value_x = fields.Many2one(comodel_name='product.attribute.value')
    value_y = fields.Many2one(comodel_name='product.attribute.value')
    product_uom_qty = fields.Float(
        string="Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
    )
