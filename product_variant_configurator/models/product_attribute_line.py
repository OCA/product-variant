# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class ProductAttributeLine(models.Model):

    _inherit = 'product.attribute.line'

    _sql_constraints = [
        ('product_attribute_uniq', 'unique(product_tmpl_id, attribute_id)',
         'The attribute already exists for this product')
    ]
