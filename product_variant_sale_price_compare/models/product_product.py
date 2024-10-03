# Copyright 2023 Emanuel Cino <ecino@compassion.ch>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    compare_fix_price = fields.Float(
        "Compare to Price",
        help="The amount will be displayed strikethroughed on the "
        "eCommerce product page",
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination,
            product_id,
            add_qty,
            pricelist,
            parent_combination,
            only_template,
        )
        product = self.env["product.product"].browse(combination_info["product_id"])
        if product.compare_fix_price:
            # This will display the discount on the website
            combination_info["has_discounted_price"] = True
            combination_info["list_price"] = product.compare_fix_price
        return combination_info
