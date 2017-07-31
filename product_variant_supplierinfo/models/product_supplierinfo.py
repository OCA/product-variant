# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product variant",
        help=("When this field is filled in, the vendor data will only"
              "apply to the variant."))

    def _check_product_template(self, vals):
        # Make a copy in case original dictionary is preferred to be kept
        vals = vals.copy()
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id
        return vals

    @api.model
    def create(self, vals):
        vals = self._check_product_template(vals)
        # templates only should have greater sequence number
        # in order to select variants in purchases.
        if not vals.get('product_id'):
            vals['sequence'] = vals.get('sequence', 10) * 10
        return super(ProductSupplierInfo, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._check_product_template(vals)
        if vals.get('sequence', None) is None:
            return super(ProductSupplierInfo, self).write(vals)
        for suppinfo in self:
            if not vals.get('product_id', suppinfo.product_id):
                vals['sequence'] *= 10
            super(ProductSupplierInfo, suppinfo).write(vals)
        return True
