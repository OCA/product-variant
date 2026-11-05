# Copyright 2021 Camptocamp SA
# Copyright 2026 Mario Castillo López <@mcastillol14>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _unarchive(self):
        self.ensure_one()
        self.write({"ptav_active": True})
        attr_val = self.product_attribute_value_id
        if not attr_val.active:
            attr_val._unarchive()
        # rebuild the tmpl_attr_line link in case it was archived too
        tmpl_attr_line = self.attribute_line_id
        vals = {"value_ids": [(4, attr_val.id, 0)]}
        if not tmpl_attr_line.active:
            # skip odoo's auto variant creation here, the variant being unarchived
            # is the same one odoo would try to create, which would violate
            # the product_product_combination_unique constraint
            tmpl_attr_line = tmpl_attr_line.with_context(
                update_product_template_attribute_values=False
            )
            vals["active"] = True
        tmpl_attr_line.write(vals)
