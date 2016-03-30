# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    loc_rack = fields.Char(string='Rack', size=16)
    loc_row = fields.Char(string='Row', size=16)
    loc_case = fields.Char(string='Case', size=16)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def write(self, vals):
        """Propagate to the variants the template storage location data
        (if modified)."""
        res = super(ProductTemplate, self).write(vals)
        vals_to_update = {}
        if ('loc_rack' in vals):
            vals_to_update['loc_rack'] = vals['loc_rack']
        if ('loc_row' in vals):
            vals_to_update['loc_row'] = vals['loc_row']
        if ('loc_case' in vals):
            vals_to_update['loc_case'] = vals['loc_case']
        if vals_to_update:
            self.mapped('product_variant_ids').write(vals_to_update)
        return res
