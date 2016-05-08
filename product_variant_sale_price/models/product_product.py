# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    @api.depends('fix_price')
    def _compute_lst_price(self):
        for product in self:
            price = product.fix_price or product.list_price
            if product.product_variant_count == 1:
                if price != product.list_price:
                    product.product_tmpl_id.write({'list_price': price})
            # else:
            #     min_price = min(product.product_tmpl_id.mapped('product_variant_ids.lst_price'))
                # product.product_tmpl_id.write({'list_price': min_price})
                # product.list_price = price
                # price = product.list_price
            # else:
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                price = uom.with_context(uom='uom')._compute_price(price)
            product.lst_price = price

    @api.multi
    def _inverse_product_lst_price(self):
        for product in self:
            vals={}
            tax = product.product_tmpl_id.taxes_id[:1]
            factor_tax = tax.price_include and (1 + tax.amount) or 1.0
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                vals['fix_price'] = uom.with_context(uom='uom')._compute_price(
                    product.lst_price)
            else:
                vals['fix_price'] = product.lst_price
            vals['impact_price'] = (
                product.lst_price / factor_tax -
                product.product_tmpl_id.list_price / factor_tax)
            product.write(vals)

    @api.multi
    @api.depends('lst_price', 'product_tmpl_id.list_price')
    def _compute_impact_price(self):
        for product in self:
            tax = product.product_tmpl_id.taxes_id[:1]
            factor_tax = tax.price_include and (1 + tax.amount) or 1.0
            product.impact_price = (
                product.lst_price / factor_tax -
                product.product_tmpl_id.list_price / factor_tax)

    lst_price = fields.Float(
        compute='_compute_lst_price',
        inverse='_inverse_product_lst_price',
    )
    fix_price = fields.Float(string='Fix Price')
    impact_price = fields.Float(
        compute='_compute_impact_price',
        string="Price Impact",
        store=True,
        digits=dp.get_precision('Product Price'))
