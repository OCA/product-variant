# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _search_on_hand(self, operator, value):
        if operator not in ["=", "!="] or not isinstance(value, bool):
            raise models.UserError(_("Operation not supported"))
        domain_loc = (
            self.env["product.product"]
            .with_context(compute_child=False)
            ._get_domain_locations()[0]
        )
        domain_loc_value = domain_loc and domain_loc[0][2] or []
        location_ids = self.env["stock.location"]._search(
            [("id", "child_of", domain_loc_value)]
        )
        quant_ids = self.env["stock.quant"]._search(
            [("location_id", "in", location_ids)]
        )
        if (operator == "!=" and value is True) or (operator == "=" and value is False):
            domain_operator = "not in"
        else:
            domain_operator = "in"
        return [("id", domain_operator, quant_ids)]
