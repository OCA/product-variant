# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def set_sale_price_on_variant(cr, registry, template_id=None):
    sql = """
        UPDATE product_product pp
        SET fix_price = pt.list_price + (
            SELECT COALESCE(SUM(pap.price_extra), 0)
            FROM product_attribute_value_product_product_rel pav_pp_rel
            LEFT JOIN product_attribute_price pap ON
                pap.value_id = pav_pp_rel.product_attribute_value_id
            WHERE pav_pp_rel.product_product_id = pp.id
            AND pap.product_tmpl_id = pt.id
        )
        FROM product_template pt
        WHERE %s;
    """ % ('pt.id = pp.product_tmpl_id' +
           (template_id and ' AND pt.id = %s' % template_id or ''))
    cr.execute(sql)
