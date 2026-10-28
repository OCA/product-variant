# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2018 Fabien Bourgeois <fabien@yaltik.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def set_sale_price_on_variant(env, template_id=None):
    # lst_price is a stored field since 20.0, so it is set along with fix_price
    sql = """
        UPDATE product_product pp
        SET fix_price = prices.price, lst_price = prices.price
        FROM (
            SELECT pp2.id, pt.id AS product_tmpl_id, pt.list_price + (
                SELECT COALESCE(SUM(ptav.price_extra), 0)
                FROM product_variant_combination pvc
                LEFT JOIN product_template_attribute_value ptav ON
                    ptav.id = pvc.product_template_attribute_value_id
                WHERE pvc.product_product_id = pp2.id
                AND ptav.product_tmpl_id = pt.id
            ) AS price
            FROM product_product pp2
            JOIN product_template pt ON pt.id = pp2.product_tmpl_id
        ) prices
        WHERE prices.id = pp.id
    """
    if template_id:
        sql += "AND prices.product_tmpl_id = %s"
        env.cr.execute(sql, (template_id,))
    else:
        env.cr.execute(sql)
