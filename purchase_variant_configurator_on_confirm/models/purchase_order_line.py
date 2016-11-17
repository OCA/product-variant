# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'product.configurator']
    _name = 'purchase.order.line'

    product_id = fields.Many2one(required=False)

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        # this method is copied from the standard onchange_product_id
        result = {}
        if not self.product_tmpl_id:
            return {}

        self.date_planned = datetime.today().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_tmpl_id.uom_po_id or\
            self.product_tmpl_id.uom_id
        result['domain'] = {
            'product_uom':
                [('category_id', '=',
                  self.product_tmpl_id.uom_id.category_id.id)]
        }

        product_lang = self.product_tmpl_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.name
        if product_lang.description_purchase:
            self.name += '\n' + self.product_tmpl_id.description_purchase

        fpos = self.order_id.fiscal_position_id
        company_id = self.env.user.company_id.id
        self.taxes_id = fpos.map_tax(
            self.product_tmpl_id.supplier_taxes_id.filtered(
                lambda r: r.company_id.id == company_id)
        )
        self._suggest_quantity_tmpl()
        self._onchange_quantity_tmpl()

        return result

    def _suggest_quantity_tmpl(self):
        # this method is copied from the standard _suggest_quantity
        if not self.product_tmpl_id:
            return

        seller_min_qty = self.product_tmpl_id.seller_ids \
            .filtered(lambda r: r.name == self.order_id.partner_id) \
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.product_qty = seller_min_qty[0].min_qty or 1.0
            self.product_uom = seller_min_qty[0].product_uom
        else:
            self.product_qty = 1.0

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity_tmpl(self):
        # this method is copied from the standard _onchange_quantity
        if not self.product_tmpl_id:
            return

        #
        seller = self.product_tmpl_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(
                DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price(
            seller.price, self.product_tmpl_id.supplier_taxes_id,
            self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and \
                seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit,
                                                    self.order_id.currency_id)

        if seller and self.product_uom and \
                seller.product_uom != self.product_uom:
            price_unit = self.env['product.uom']._compute_price(
                seller.product_uom.id, price_unit,
                to_uom_id=self.product_uom.id)

        self.price_unit = price_unit
