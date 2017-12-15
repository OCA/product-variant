# -*- coding: utf-8 -*-
# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models


class ProductAttributeLine(models.Model):
    _inherit = 'product.attribute.line'

    required = fields.Boolean('Required', default=True)

    _sql_constraints = [
        ('product_attribute_uniq', 'unique(product_tmpl_id, attribute_id)',
         'The attribute already exists for this product')
    ]
