# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if (
                "template_name" in self._context
                and "create_product_product" in self._context
            ):
                vals["name"] = self._context["template_name"]
        return super().create(vals_list)

    def _prepare_variant_values(self, combination):
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict["name"] = self.name
        return variant_dict
