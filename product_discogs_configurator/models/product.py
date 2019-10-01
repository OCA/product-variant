# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, api
from .discogs import DISCOGS_URL


class ProductTemplate(models.Model):

    _name = 'product.template'
    _inherit = ['product.template', 'discogs.mixin']

    @api.depends('discogs_id')
    def _compute_discogs_url(self):
        for product in self:
            product.discogs_url = '%s/master/%s' % (
                DISCOGS_URL, product.discogs_id
            )


class ProductProduct(models.Model):

    _name = 'product.product'
    _inherit = ['product.product', 'discogs.mixin']

    @api.depends('discogs_id')
    def _compute_discogs_url(self):
        for product in self:
            product.discogs_url = '%s/release/%s' % (
                DISCOGS_URL, product.discogs_id
            )
