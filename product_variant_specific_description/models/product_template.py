# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    description = fields.Html(
        compute="_compute_description",
        inverse="_inverse_description",
    )
    is_system_multi_lang = fields.Boolean(
        compute="_compute_is_system_multi_lang",
    )

    def _compute_is_system_multi_lang(self):
        is_multi_lang = self.env["res.lang"].search_count([]) > 1
        for rec in self:
            rec.is_system_multi_lang = is_multi_lang

    def _prepare_variant_values(self, combination):
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict["description"] = self.description
        return variant_dict

    @api.depends_context("lang")
    @api.depends("product_variant_ids", "product_variant_ids.description")
    def _compute_description(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.description = template.product_variant_ids.description
        for template in self - unique_variants:
            template.description = None

    def _inverse_description(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.description = template.description

    def open_product_variant(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.product",
            "view_mode": "form",
            "res_id": self.product_variant_id.id,
        }
