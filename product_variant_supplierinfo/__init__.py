# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from . import models
from openerp import SUPERUSER_ID


def duplicate_supplierinfo_per_variant(cr, registry):
    """Duplicate supplierinfo for each product variant."""
    supp_info_obj = registry['product.supplierinfo']
    supp_info_ids = supp_info_obj.search(cr, SUPERUSER_ID, [])
    for supp_info in supp_info_obj.browse(cr, SUPERUSER_ID, supp_info_ids):
        first = True
        for product in supp_info.product_tmpl_id.product_variant_ids:
            if first:
                supp_info_obj.write(
                    cr, SUPERUSER_ID, supp_info.id, {'product_id': product.id})
                first = False
            else:
                supp_info_obj.copy(
                    cr, SUPERUSER_ID, supp_info.id, {'product_id': product.id})
