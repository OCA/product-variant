# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """This post-init-hook will update all existing product.product weight"""
    cr.execute("""UPDATE product_product
                  SET weight = product_template.weight
                  FROM product_template
                    WHERE product_template.id = product_product.product_tmpl_id
                    AND (product_product.weight = 0 OR
                            product_product.weight IS NULL);
                  """)

    cr.execute("""UPDATE product_product
        SET weight_net = product_template.weight
        FROM product_template
          WHERE product_template.id = product_product.product_tmpl_id
          AND (product_product.weight_net = 0 OR
                product_product.weight_net IS NULL);
        """)
