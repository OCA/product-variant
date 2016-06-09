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
        obj = self.with_context(bypass_down_write=True,
                                bypass_template_history=True)
        res = super(ProductTemplate, obj).create_variant_ids()
        return res

    @api.multi
    def write(self, vals):
        """Propagate to the variants the template cost price (if modified)."""
        res = super(ProductTemplate, self).write(vals)
        if ('standard_price' in vals and
                not self.env.context.get('bypass_down_write')):
            self.mapped('product_variant_ids').with_context(
                bypass_template_history=True).write(
                {'standard_price': vals['standard_price']})
        return res


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    @api.model
    def create(self, values):
        if self.env.context.get('bypass_template_history'):
            return self
        return super(ProductPriceHistory, self).create(values)
