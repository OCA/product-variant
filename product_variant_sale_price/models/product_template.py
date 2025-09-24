# Copyright 2016 Tecnativa - Sergio Teruel
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models
from odoo.tools import config


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _prepare_variant_values(self, combination):
        values = super()._prepare_variant_values(combination)
        values["fix_price"] = self.list_price
        return values

    def _create_variant_ids(self):
        res = super()._create_variant_ids()
        for tmpl in self:
            tmpl.product_variant_ids.with_context(skip_update_fix_price=True).write(
                {"fix_price": tmpl.list_price}
            )
        return res

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("skip_update_fix_price", False):
            return res
        if "list_price" in vals:
            self.mapped("product_variant_ids").write({"fix_price": vals["list_price"]})
        return res

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        parent_combination=False,
        only_template=False,
    ):
        res = super()._get_combination_info(
            combination,
            product_id,
            add_qty,
            parent_combination,
            only_template,
        )
        test_condition = not config["test_enable"] or (
            config["test_enable"]
            and self.env.context.get("test_product_variant_sale_price")
        )
        if test_condition:
            res["price_extra"] = 0.0
        return res
