# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'
    uos_id = fields.Many2one(
        'product.uom', 'Unit of Sale',
        help='Specify a unit of measure here if invoicing is made in another '
             'unit of measure than inventory. Keep empty to use the default '
             'unit of measure.')
    uos_coeff = fields.Float(
        'Unit of Measure -> UOS Coeff',
        digits_compute=dp.get_precision('Product UoS'),
        help='Coefficient to convert default Unit of Measure to Unit of Sale\n'
             ' uos = uom * coeff')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        """Propagate to the variants the template UoS (if modified)."""
        res = super(ProductTemplate, self).write(vals)
        if ('uos_id' in vals):
            self.mapped('product_variant_ids').write(
                {'uos_id': vals['uos_id']})
        if ('uos_coeff' in vals):
            self.mapped('product_variant_ids').write(
                {'uos_coeff': vals['uos_coeff']})
        return res
