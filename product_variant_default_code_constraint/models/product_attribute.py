# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", _("Attribute code must be unique!"))
    ]
