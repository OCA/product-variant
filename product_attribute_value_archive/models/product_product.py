# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _unarchive_tmpl_attr_vals(self):
        """Unarchives related `product_attribute_value` and
        `product_template_attribute_value`.
        """
        tmpl_attr_vals = self.mapped("product_template_attribute_value_ids")
        archived_tmpl_attr_vals = tmpl_attr_vals.filtered(lambda v: not v.ptav_active)
        for tmpl_attr_val in archived_tmpl_attr_vals:
            tmpl_attr_val._unarchive()

    def write(self, values):
        res = super().write(values)
        to_unarchive = values.get("active")
        if to_unarchive:
            self._unarchive_tmpl_attr_vals()
        return res
