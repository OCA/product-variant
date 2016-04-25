# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_is_variant(self):
        print self.env.context
        if self.env.context.get('active_model') != 'product.template':
            self.is_variant = True

    is_variant = fields.Boolean(compute='_compute_is_variant')


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _product_lst_price(self):
        for product in self:
            if 'uom' in self.env.context:
                uom = product.uos_id or product.uom_id
                price = uom.with_context(uom='uom')._compute_price(
                    product.lst_price)
            else:
                price = product.lst_price
            product.lst_price = price

    @api.multi
    def _set_product_lst_price(self):
        if 'uom' in self.env.context:
            uom = self.uos_id or self.uom_id
            self.lst_price = uom.with_context(uom='uom')._compute_price(
                self.lst_price)
        # return {'lst_price': self.lst_price}

    lst_price = fields.Float(
        compute='_product_lst_price',
        inverse='_set_product_lst_price',
        store=True,
    )
