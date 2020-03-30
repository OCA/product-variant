# Copyright 2020 Druidoo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    description_sale = fields.Text(
        "Description Sale",
        translate=True,
        help=(
            "A description of the Product that you want to communicate to "
            "your customers. This description will be copied to every "
            "Sales Order, Delivery Order and Customer Invoice/Credit Note"
        ),
    )
