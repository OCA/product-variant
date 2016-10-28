# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models, _
from openerp.tools.float_utils import float_compare
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'product.configurator']
    _name = 'purchase.order.line'

    product_id = fields.Many2one(required=False)

    @api.multi
    def action_duplicate(self):
        self.ensure_one()
        self.copy()

    @api.multi
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        new_value = self.onchange_product_id_product_configurator()
        value = res.setdefault('value', {})
        value.update(new_value)
        if self.product_id:
            if self.product_id.description_purchase:
                value['name'] += '\n' + self.product_id.description_purchase
        return res

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if not self.product_tmpl_id:
            return {}
        res = super(PurchaseOrderLine, self).onchange_product_tmpl_id()
        if self.product_tmpl_id.description_purchase:
            self.name += '\n' + self.product_tmpl_id.description_purchase

        self.product_uom = self.product_tmpl_id.uom_po_id \
                           or self.product_tmpl_id.uom_id

        # Get planned date and min quantity
        supplierinfo = False
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for supplier in self.product_tmpl_id.seller_ids:
            if supplier.name == self.order_id.partner_id:
                supplierinfo = supplier
                if supplierinfo.product_uom != self.product_uom:
                    res['warning'] = {
                        'title': _('Warning!'),
                        'message': _('The selected supplier only sells this '
                                     'product by %s') % (
                            supplierinfo.product_uom.name)
                    }
                min_qty = supplierinfo.product_uom._compute_qty(
                    supplierinfo.product_uom.id, supplierinfo.min_qty,
                    to_uom_id=self.product_uom.id)
                # If the supplier quantity is greater than entered from user,
                # set minimal.
                if (float_compare(
                        min_qty, self.product_qty,
                        precision_digits=precision) == 1):
                    if self.product_qty:
                        res['warning'] = {
                            'title': _('Warning!'),
                            'message': _('The selected supplier has a minimal '
                                         'quantity set to %s %s, you should '
                                         'not purchase less.') % (
                                supplierinfo.min_qty,
                                supplierinfo.product_uom.name)
                        }
                    self.product_qty = min_qty
        if not self.date_planned and supplierinfo:
            dt = fields.Datetime.to_string(
                self._get_date_planned(supplierinfo, self.order_id))
            self.date_planned = dt
        # Get taxes
        taxes = self.product_tmpl_id.supplier_taxes_id
        self.taxes_id = self.order_id.fiscal_position_id.map_tax(taxes)
        return res
