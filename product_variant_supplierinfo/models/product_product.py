# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    seller_ids = fields.One2many(comodel_name="product.supplierinfo",
                                 inverse_name='product_id')
