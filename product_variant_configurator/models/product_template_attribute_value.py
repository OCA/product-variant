# Copyright 2020 ForgeFlow S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3
from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _get_combination_name(self):
        """Overwritten method to avoid:
        Exclude values from single value lines or from no_variant attributes."""
        return ", ".join([ptav.name for ptav in self._filter_single_value_lines()])
