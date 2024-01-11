# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import models


class View(models.Model):
    _inherit = "ir.ui.view"

    def _postprocess_tag_groupby(self, node, name_manager, node_info):
        """Solves a recursion problem caused when the groupby refers to a
        field of a many2one model, and that model also has the same field name.
        In this example, the stock.valuation.layer.tree view contains a groupby
        product_id, and the product.product model already has a product_id field,
        relating to the same model. Without this code we would reach a recursion error."""
        name = node.get("name")
        if name_manager.model._name == "product.product" and name == "product_id":
            return
        return super()._postprocess_tag_groupby(node, name_manager, node_info)
