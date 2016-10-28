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
            product_lang = self.product_id.with_context({
                'lang': self.partner_id.lang,
                'partner_id': self.partner_id.id,
            })
            if product_lang.description_purchase:
                value['name'] += '\n' + self.product_id.description_purchase
        return res

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if not self.product_tmpl_id:
            return {}

        result = super(PurchaseOrderLine, self).onchange_product_tmpl_id()

        self.date_planned = datetime.today().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_tmpl_id.uom_po_id\
            or self.product_tmpl_id.uom_id
        result['domain'] = {
            'product_uom':
            [('category_id', '=', self.product_tmpl_id.uom_id.category_id.id)]
        }

        product_lang = self.product_tmpl_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        if product_lang.description_purchase:
            self.name += '\n' + self.product_tmpl_id.description_purchase

        fpos = self.order_id.fiscal_position_id
        company_id = self.env.user.company_id.id
        self.taxes_id = fpos.map_tax(
            self.product_id.supplier_taxes_id.filtered(
                lambda r: r.company_id.id == company_id)
        )
        self._suggest_quantity()
        self._onchange_quantity()
        return result
