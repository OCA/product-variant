# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """Create and populate product variant name column BEFORE Odoo adds constraints"""
    logger.info("Pre-init: Creating name column on product_product")
    env.cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='product_product' AND column_name='name';
        """
    )

    if not env.cr.fetchone():
        env.cr.execute(
            """
            ALTER TABLE product_product
            ADD COLUMN name JSONB;
            """
        )

        logger.info("Pre-init: Populating product variant names from templates")
        env.cr.execute(
            """
            UPDATE product_product pp
            SET name = pt.name
            FROM product_template pt
            WHERE pp.product_tmpl_id = pt.id;
            """
        )
