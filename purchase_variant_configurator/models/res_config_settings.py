# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    po_confirm_create_variant = fields.Boolean(
        related="company_id.po_confirm_create_variant", readonly=False
    )
