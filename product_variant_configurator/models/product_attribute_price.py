# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductAttributePrice(models.Model):

    _inherit = 'product.attribute.price'

    attribute_id = fields.Many2one(
        string='Attribute',
        comodel_name='product.attribute',
        related='value_id.attribute_id')
