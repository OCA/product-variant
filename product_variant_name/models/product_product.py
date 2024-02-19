# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    name = fields.Char(index="trigram", required=True, translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        new_products = self.env["product.product"]
        for vals in vals_list:
            if "name" in vals:
                new_products |= super(
                    ProductProduct, self.with_context(template_name=vals["name"])
                ).create([vals])
                vals_list.remove(vals)
        new_products |= super().create(vals_list)
        return new_products
