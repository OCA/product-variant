# -*- coding: utf-8 -*-
# Copyright 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    """
    This post-init-hook will update all existing product.product
    available_in_pos
    """
    cr.execute(
        """
        UPDATE product_product
        SET available_in_pos = product_template.available_in_pos
        FROM product_template
        WHERE product_template.id = product_product.product_tmpl_id
        """)
