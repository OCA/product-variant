# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    seller_ids = fields.One2many(comodel_name="product.supplierinfo",
                                 inverse_name='product_id')
