# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def _update_available_in_pos(self, vals):
        if 'available_in_pos' in vals:
            self.mapped('product_variant_ids').write({
                'available_in_pos': vals['available_in_pos']})

    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        self._update_available_in_pos(vals)
        return res
