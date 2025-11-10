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

    prefix_as_default_code = fields.Boolean(
        string="Reference Prefix as default Reference",
        default=False,
        config_parameter="product_variant_default_code.prefix_as_default_code",
    )

    sequence_as_default_code = fields.Many2one(
        string="Default sequence as default Reference",
        comodel_name="ir.sequence",
        config_parameter="product_variant_default_code.sequence_as_default_code",
    )

    use_sequence_per_product_tmp_as_default_code = fields.Boolean(
        string="Use specific sequence par Product in Reference",
        config_parameter="product_variant_default_code."
        "use_sequence_per_product_tmp_as_default_code",
    )
