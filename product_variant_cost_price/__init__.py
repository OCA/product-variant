# -*- coding: utf-8 -*-
# (c) 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from . import models
from openerp import SUPERUSER_ID


def load_cost_price_on_variant(cr, registry):
    product_obj = registry['product.product']
    product_ids = product_obj.search(cr, SUPERUSER_ID, [])
    for product in product_obj.browse(cr, SUPERUSER_ID, product_ids):
        product_obj.write(
            cr, SUPERUSER_ID, product.id,
            {'standar_price': product.product_tmpl_id.standard_price,
             'cost_method': product.product_tmpl_id.cost_method})
