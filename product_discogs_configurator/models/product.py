# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class ProductTemplate(models.Model):

    _name = 'product.template'
    _inherit = ['product.template', 'discogs.mixin']


class ProductProduct(models.Model):

    _name = 'product.product'
    _inherit = ['product.product', 'discogs.mixin']
