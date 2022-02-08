# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class Product(models.Model):
    _inherit = "product.product"

    additional_tax_ids = fields.Many2many(
        comodel_name="account.tax",
        string="Variant Taxes",
        domain=[("type_tax_use", "=", "sale")],
        help="Additional taxes specific to this variant",
    )
