# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_product_variant_count_all(self):
        for rec in self:
            rec.product_variant_count_all = (
                self.with_context(active_test=False)
                .env["product.product"]
                .search_count([("product_tmpl_id", "=", rec.id)])
            )

    product_variant_count_all = fields.Integer(
        "Inactive variants", compute="_compute_product_variant_count_all"
    )
    active = fields.Boolean(compute="_compute_active", readonly=False, store=True)

    def write(self, vals):
        if vals.get("active"):
            self = self.with_context(skip_reactivate_variant=False)
        return super().write(vals)

    def _create_variant_ids(self):
        if "skip_reactivate_variant" not in self._context:
            self = self.with_context(skip_reactivate_variant=True)
        self = self.with_context(unset_combination_deleted=True)
        return super()._create_variant_ids()

    @api.depends("product_variant_ids.active")
    def _compute_product_variant_count(self):
        return super()._compute_product_variant_count()

    @api.depends("product_variant_ids.active")
    def _compute_active(self):
        for template in self:
            if not template.product_variant_ids.mapped("active"):
                template.active = False
            else:
                template.active = True
