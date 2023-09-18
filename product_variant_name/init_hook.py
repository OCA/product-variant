# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Init product variant name with product template name"""
    logger.info("Setting product variant name with product template name")
    cr.execute(
        """
        UPDATE product_product pp
        SET name = pt.name
        FROM product_template pt
        WHERE pp.product_tmpl_id = pt.id;
        """
    )
