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

    related_sequence = fields.Integer(
        String='Sequence',
        related="sequence",
        help=("Allows to modify the sequence manually because "
              "the sequence field is difficult to modify because 'handle'."))

    def _check_product_template(self, vals):
        # Make a copy in case original dictionary is preferred to be kept
        vals = vals.copy()
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id
        return vals

    @api.model
    def _get_sequence_related(self, vals):
        """
            In purchase orders, we want to get the product_supplierinfo
            associated with the product variant.
            But in Odoo, it's the product_supplierinfo which has the
            smallest sequence that is used.
            That's why, we put a low sequence to the product_supplierinfo
            of the product variant than the product template.
        """
        product_id = vals.get('product_id', self.product_id)
        product_tmpl_id = vals.get('product_tmpl_id', self.product_tmpl_id)
        related_sequence = 15
        if product_id:
            related_sequence = 5
        elif product_tmpl_id:
            related_sequence = 10
        return related_sequence

    @api.model
    def create(self, vals):
        vals = self._check_product_template(vals)
        vals.update({
            'related_sequence': self._get_sequence_related(vals),
        })
        return super(ProductSupplierInfo, self).create(vals)

    @api.multi
    def write(self, vals):
        vals = self._check_product_template(vals)
        for item in self:
            if 'product_id' in vals:
                vals['related_sequence'] = item._get_sequence_related(
                    vals)
        return super(ProductSupplierInfo, self).write(vals)
