# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class Product(models.Model):
    _inherit = "product.product"

    def action_open_product_quants(self):
        action = super().action_open_quants()
        action.update(name=_("%s - Update Quantity", self.display_name))
        return action
