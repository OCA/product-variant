# Copyright 2015-17 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_description_sale = fields.Text(
        string="Variant Sale Description",
        help="A description of the product variant that you want to "
        "communicate to your customers."
        "This description will be copied to every Sale Order",
        translate=True,
    )
