# Copyright 2017 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseConfiguration(models.TransientModel):
    _inherit = "res.config.settings"

    group_product_default_code_manual_mask = fields.Boolean(
        string="Product Default Code Manual Mask",
        default=False,
        help="Set behaviour of codes. Default: Automask"
        " (depends on variant use: "
        "see Sales/Purchases configuration)",
        implied_group="product_variant_default_code"
        ".group_product_default_code_manual_mask",
    )
