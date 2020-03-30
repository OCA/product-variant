# Copyright 2020 Druidoo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    description_sale = fields.Text(
        compute='_compute_description_sale',
        inverse='_inverse_description_sale',
        search='_search_description_sale',
    )

    def _inverse_description_sale(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.description_sale = self.description_sale

    def _search_description_sale(self, operator, value):
        return [('product_variant_ids.description_sale', operator, value)]

    @api.depends('product_variant_ids.description_sale')
    def _compute_description_sale(self):
        for rec in self:
            if len(rec.product_variant_ids) == 1:
                rec.description_sale = rec.product_variant_ids.description_sale
            else:
                rec.description_sale = False
