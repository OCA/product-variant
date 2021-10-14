# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class PurchaseManageVariant(models.TransientModel):
    _name = 'purchase.manage.variant'
    _description = 'Add or modify variants on purchase order lines'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string="Template", required=True)
    # This is a many2many because Odoo fails to fill one2many in onchanges
    variant_line_ids = fields.Many2many(
        comodel_name='purchase.manage.variant.line',
        string="Variant Lines")

    def _get_product_variant(self, value_x, value_y):
        """Filter the corresponding product for provided values."""
        self.ensure_one()
        values = value_x
        if value_y:
            values += value_y
        return self.product_tmpl_id.product_variant_ids.filtered(
            lambda x: not (values - x.attribute_value_ids)
        )[:1]

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.variant_line_ids = [(6, 0, [])]
        template = self.product_tmpl_id
        context = self.env.context
        record = self.env[context['active_model']].browse(
            context['active_id'])
        if context['active_model'] == 'purchase.order.line':
            purchase_order = record.order_id
        else:
            purchase_order = record
        attr_lines = template.attribute_line_ids.filtered(
            lambda x: x.attribute_id.create_variant != 'no_variant'
        )
        num_attrs = len(attr_lines)
        if not template or not attr_lines or num_attrs > 2:
            return
        line_x = attr_lines[0]
        line_y = False if num_attrs == 1 else attr_lines[1]
        lines = []
        for value_x in line_x.value_ids:
            for value_y in line_y and line_y.value_ids or [False]:
                product = self._get_product_variant(value_x, value_y)
                if not product:
                    continue
                order_line = purchase_order.order_line.filtered(
                    lambda x: x.product_id == product
                )[:1]
                lines.append((0, 0, {
                    'value_x': value_x,
                    'value_y': value_y,
                    'product_uom_qty': order_line.product_qty,
                }))
        self.variant_line_ids = lines

    @api.multi
    def button_transfer_to_order(self):
        context = self.env.context
        record = self.env[context['active_model']].browse(context['active_id'])
        if context['active_model'] == 'purchase.order.line':
            purchase_order = record.order_id
        else:
            purchase_order = record
        OrderLine = self.env['purchase.order.line']
        lines2unlink = OrderLine
        lines2create = []
        for line in self.variant_line_ids:
            product = self._get_product_variant(line.value_x, line.value_y)
            order_line = purchase_order.order_line.filtered(
                lambda x: x.product_id == product
            )
            if order_line:
                if not line.product_uom_qty:
                    # Done this way because there's a side effect removing here
                    lines2unlink |= order_line
                else:
                    order_line.product_qty = line.product_uom_qty
            elif line.product_uom_qty:
                order_line = OrderLine.new({
                    'product_id': product.id,
                    'product_uom': product.uom_id,
                    'product_uom_qty': line.product_uom_qty,
                    'order_id': purchase_order.id,
                })
                order_line.onchange_product_id()
                # This should be done later for handling supplier quantities
                order_line.product_qty = line.product_uom_qty
                order_line._onchange_quantity()
                order_line_vals = order_line._convert_to_write(
                    order_line._cache)
                lines2create.append((0, 0, order_line_vals))
        if lines2create:
            purchase_order.write({'order_line': lines2create})

        lines2unlink.unlink()


class PurchaseManageVariantLine(models.TransientModel):
    _name = 'purchase.manage.variant.line'
    _description = 'Define variants quantities on purchase order lines'

    value_x = fields.Many2one(comodel_name='product.attribute.value')
    value_y = fields.Many2one(comodel_name='product.attribute.value')
    product_uom_qty = fields.Float(
        string="Quantity", digits=dp.get_precision('Product UoS'),
    )
