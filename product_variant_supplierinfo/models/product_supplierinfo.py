# -*- coding: utf-8 -*-
# © 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    product_id = fields.Many2one(
        comodel_name='product.product', string="Product variant",
        required=True)

    def _check_product_template(self, vals):
        # Make a copy in case original dictionary is preferred to be kept
        vals = vals.copy()
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id
        elif vals.get('product_tmpl_id'):
            product = self.env['product.product'].search(
                [('product_tmpl_id', '=', vals['product_tmpl_id'])])
            if product:
                vals['product_id'] = product[0].id
        return vals

    @api.model
    def create(self, vals):
        vals = self._check_product_template(vals)
        return super(ProductSupplierInfo, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._check_product_template(vals)
        return super(ProductSupplierInfo, self).write(vals)
