# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    po_confirm_create_variant = fields.Boolean(
        string="Create variants on confirm",
        help="Create product variants when confirming",
        default=False,
    )
