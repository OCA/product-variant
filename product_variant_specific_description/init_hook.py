# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    logger.info("Setting product variant description with product template description")
    cr.execute(
        """
        UPDATE product_product pp
        SET description = pt.description
        FROM product_template pt
        WHERE pp.product_tmpl_id = pt.id;
        """
    )
