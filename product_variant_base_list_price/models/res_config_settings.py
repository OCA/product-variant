# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    price_display_variant_pricelist_id = fields.Many2one(
        related="company_id.price_display_variant_pricelist_id",
        readonly=False,
    )
