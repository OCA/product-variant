# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'list_price' in vals:
            for product in self:
                for variant in product.mapped('product_variant_ids'):
                    variant._onchange_lst_price()
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    @api.depends('fix_price')
    def _compute_lst_price(self):
        for product in self:
            price = product.fix_price or product.list_price
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                price = uom._compute_price(
                    product.uom_id.id, price, self.env.context['uom'])
            product.lst_price = price

    @api.multi
    def _inverse_product_lst_price(self):
        for product in self:
            vals={}
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                vals['fix_price'] = uom._compute_price(product.uom_id.id,
                    product.lst_price, self.env.context['uom'])
            else:
                vals['fix_price'] = product.lst_price
            product.write(vals)

    lst_price = fields.Float(
        compute='_compute_lst_price',
        inverse='_inverse_product_lst_price',
    )
    fix_price = fields.Float(string='Fix Price')
