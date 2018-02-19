# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba <alex.comba@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """
    This post-init-hook will update only product.product
    sale_delay values in case they are not set
    """
    cr.execute(
        """
        UPDATE product_product
        SET sale_delay = product_template.sale_delay
        FROM product_template
        WHERE product_template.id = product_product.product_tmpl_id
        AND product_product.sale_delay IS NULL
        """)
