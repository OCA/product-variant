# Copyright 2026 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def pre_init_hook(env):
    env.cr.execute(
        """
        ALTER TABLE product_attribute_value
        ADD COLUMN IF NOT EXISTS code varchar
        """
    )


def post_init_hook(env):
    values = env["product.attribute.value"].search([("code", "=", False)])
    for value in values:
        value.code = value.name[:2] if value.name else ""
