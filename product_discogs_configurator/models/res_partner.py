# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, api
from .discogs import DISCOGS_URL


class ProductTemplate(models.Model):

    _name = 'res.partner'
    _inherit = ['res.partner', 'discogs.mixin']

    @api.depends('discogs_id')
    def _compute_discogs_url(self):
        for partner in self:
            if partner.is_artist:
                partner.discogs_url = '%s/artist/%s' % (
                    DISCOGS_URL, partner.discogs_id
                )
            if partner.is_label:
                partner.discogs_url = '%s/label/%s' % (
                    DISCOGS_URL, partner.discogs_id
                )
