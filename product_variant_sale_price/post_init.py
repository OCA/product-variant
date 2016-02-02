# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import SUPERUSER_ID


def post_init_hook(cr, registry):
    """
    Post-install script. Because 'lst_price' has been replaced by
    'variant_lst_price, we should be able to retrieve its values
    and use them to fill the new fields.
    """
    product_obj = registry['product.product']
    product_ids = product_obj.search(cr, SUPERUSER_ID, [])
    for product in product_obj.browse(cr, SUPERUSER_ID, product_ids):
        cr.execute("UPDATE product_product "
                   "SET variant_lst_price = %s",
                   (product.lst_price,))
