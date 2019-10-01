# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models, fields


class DiscogsMixin(models.AbstractModel):

    _name = 'discogs.mixin'

    discogs_id = fields.Integer()
