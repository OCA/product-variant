# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    without_prefix = env["product.template"].search([("code_prefix", "=", False)])
    for tmpl in without_prefix:
        tmpl.code_prefix = f"Default_{tmpl.id}/"
    env["product.template"].flush()

    attr_without_code = env["product.attribute"].search([("code", "=", False)])
    for attr in attr_without_code:
        attr.code = f"Default_{attr.id}/"
    env["product.attribute"].flush()

    val_without_code = env["product.attribute.value"].search([("code", "=", False)])
    for val in val_without_code:
        val.code = f"Default_{val.id}/"
    env["product.attribute.value"].flush()
