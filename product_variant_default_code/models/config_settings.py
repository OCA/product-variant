# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    group_product_default_code = fields.Selection([
        (0, 'Automask'),
        (1, 'Manual Mask')],
        string='Product Default Code behaviour',
        help='Set behaviour of codes (depends on variant use: '
             'see Sales/Purchases configuration)',
        implied_group='product_variant_default_code'
                      '.group_product_default_code',
    )
