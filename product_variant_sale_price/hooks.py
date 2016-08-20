# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def set_sale_price_on_variant(cr, registry):
    sql = """
        UPDATE product_product pp
        SET fix_price = (
            SELECT (pt.list_price + (SELECT COALESCE( SUM(pap.price_extra), 0)
                    FROM product_attribute_value_product_product_rel pav_pp_rel
                    LEFT JOIN product_attribute_price pap ON
                        pap.value_id = pav_pp_rel.att_id
                    LEFT JOIN product_product pp_rel ON
                        pav_pp_rel.prod_id = pp_rel.id
                    LEFT JOIN product_template pt ON
                        pp_rel.product_tmpl_id = pt.id
                    WHERE pav_pp_rel.prod_id = pp.id AND
                        pap.product_tmpl_id = pt.id
                )) AS sum_price_extra
            FROM product_product pp_in LEFT JOIN product_template pt ON
                pp_in.product_tmpl_id=pt.id
            WHERE pp_in.id = pp.id
        );
    """
    cr.execute(sql)
