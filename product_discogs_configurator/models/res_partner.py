# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductTemplate(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'discogs.mixin']
