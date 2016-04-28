# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def set_sale_price_on_variant(cr, registry):
    sql = """
            UPDATE product_product pp
            SET fix_price = (SELECT list_price
                                FROM product_template pt
                                WHERE pp.product_tmpl_id = pt.id)
    """
    cr.execute(sql)
