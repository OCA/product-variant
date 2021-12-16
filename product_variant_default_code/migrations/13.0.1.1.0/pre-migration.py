# Copyright 2021 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

xmlid_renames_res_groups = [
    (
        "product_variant_default_code.group_product_default_code",
        "product_variant_default_code.group_product_default_code_manual_mask",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, xmlid_renames_res_groups)
