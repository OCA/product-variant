# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class ProductProduct(models.Model):
    _inherit = "product.template"

    @api.multi
    @api.onchange('list_price')
    def _compute_variant_price(self):
        pass


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    @api.depends('fix_price')
    def _compute_lst_price(self):
        for product in self:
            if product.product_variant_count == 1:
                price = product.list_price
            else:
                price = product.fix_price or product.list_price
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                price = uom.with_context(uom='uom')._compute_price(price)
            product.lst_price = price

    @api.multi
    def _inverse_product_lst_price(self):
        for product in self:
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                product.fix_price = uom.with_context(uom='uom')._compute_price(
                    product.lst_price)
            else:
                product.fix_price = product.lst_price

    lst_price = fields.Float(
        compute='_compute_lst_price',
        inverse='_inverse_product_lst_price',
    )

    fix_price = fields.Float(string='Fix Price')
    impact_price = fields.Float(string="Price Impact",
                            digits=dp.get_precision('Product Price'))
