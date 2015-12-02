# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def create_variant_ids(self):
        """Write in the new created variants the current template cost price.
        """
        variants_per_template = {}
        for template in self:
            variants_per_template[template] = (
                template.standard_price, template.product_variant_ids)
        obj = self.with_context(bypass_down_write=True)
        res = super(ProductTemplate, obj).create_variant_ids()
        for template in self:
            (template.product_variant_ids -
             variants_per_template[template][1]).write(
                {'standard_price': variants_per_template[template][0]})
        return res

    @api.multi
    def write(self, vals):
        """Propagate to the variants the template cost price (if modified)."""
        res = super(ProductTemplate, self).write(vals)
        if ('standard_price' in vals and
                not self.env.context.get('bypass_down_write')):
            self.mapped('product_variant_ids').write(
                {'standard_price': vals['standard_price']})
        return res
