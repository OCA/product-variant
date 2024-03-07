# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLine(models.Model):

    _inherit = ["account.move.line", "product.configurator"]
    _name = "account.move.line"
