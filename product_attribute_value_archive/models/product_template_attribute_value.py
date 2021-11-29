# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _unarchive(self):
        """Unarchive
        """
        self.ensure_one()
        self.write({"ptav_active": True})
        # get related archived product_attribute_value and unarchive it
        attr_val = self.product_attribute_value_id
        if not attr_val.active:
            attr_val._unarchive()
        # Rebuild the product_template_attribute_line link if it has been
        # archived.
        tmpl_attr_line = self.attribute_line_id
        vals = {"value_ids": [(4, attr_val.id, 0)]}
        if not tmpl_attr_line.active:
            # As soon as we unarchive the product_template_attribute_line,
            # odoo will try to create new variants, which we don't want here.
            # If this code is executed, it is because a variant is about
            # to be unarchived (the same that odoo will try to create),
            # which would violate the "product_product_combination_unique"
            # constaint.
            # Set the update_product_template_attribute_values context key
            # to disable this.
            tmpl_attr_line = tmpl_attr_line.with_context(
                update_product_template_attribute_values=False
            )
            vals["active"] = True
        tmpl_attr_line.write(vals)
