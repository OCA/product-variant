# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields, api


DISCOGS_URL = 'https://www.discogs.com'


class DiscogsMixin(models.AbstractModel):

    _name = 'discogs.mixin'

    discogs_id = fields.Integer(string='Discogs ID')
    discogs_url = fields.Char(compute='_compute_discogs_url')

    @api.depends('discogs_id')
    def _compute_discogs_url(self):
        raise NotImplementedError

    def open_discogs_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.discogs_url,
            'target': 'self',
        }
