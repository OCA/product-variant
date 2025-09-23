# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging


def pre_init_hook(cr):
    logger = logging.getLogger(__name__)
    logger.info("Add product_product.manual_code column if it does not yet exist")
    cr.execute(
        "ALTER TABLE product_product ADD COLUMN IF NOT EXISTS manual_code BOOLEAN;"
    )
    cr.execute("UPDATE product_product SET manual_code = TRUE;")
    logger.info("product_product.manual_code set to True on existing variants")
