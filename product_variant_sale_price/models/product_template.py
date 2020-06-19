# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_fix_price(self, vals):
        if 'list_price' in vals:
            self.mapped('product_variant_ids').write({
                'fix_price': vals['list_price']})

    @api.model
    def create(self, vals):
        product_tmpl = super(ProductTemplate, self).create(vals)
        product_tmpl._update_fix_price(vals)
        return product_tmpl

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if self.env.context.get('skip_update_fix_price', False):
            return res
        for template in self:
            template._update_fix_price(vals)
        return res
