# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """This post-init-hook will update all existing product.product weight"""
    cr.execute("""UPDATE product_product pp
                  SET weight = pt.weight, weight_net = pt.weight_net
                  FROM product_template pt
                  WHERE pt.id = pp.product_tmpl_id;
              """)
