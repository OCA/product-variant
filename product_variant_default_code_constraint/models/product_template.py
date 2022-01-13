# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    code_prefix = fields.Char(
        required=True,
    )

    _sql_constraints = [
        (
            "code_prefix_uniq",
            "unique(code_prefix)",
            _("Product code_prefix must be unique!"),
        )
    ]
