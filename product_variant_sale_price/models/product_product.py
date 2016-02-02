# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields
from openerp.addons import decimal_precision as dp


class ProductProduct(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'variant_lst_price': fields.float(
            'Variant Sale Price',
            digits_compute=dp.get_precision('Product Price'),
            help="Variant specific price, it can be used in pricelists"),
    }
