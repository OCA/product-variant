# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'
    weight = fields.Float(
        'Gross Weight', digits_compute=dp.get_precision('Stock Weight'),
        help="The gross weight in Kg.")
    weight_net = fields.Float(
        'Net Weight', digits_compute=dp.get_precision('Stock Weight'),
        help="The net weight in Kg.")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        """Propagate to the variants the template weights (if modified)."""
        res = super(ProductTemplate, self).write(vals)
        if ('weight' in vals):
            self.mapped('product_variant_ids').write(
                {'weight': vals['weight']})
        if ('weight_net' in vals):
            self.mapped('product_variant_ids').write(
                {'weight_net': vals['weight_net']})
        return res
