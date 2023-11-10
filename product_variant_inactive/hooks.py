from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    product_variant_action = env.ref(
        "product.product_variant_action", raise_if_not_found=False
    )
    product_variant_action.write(
        {
            "domain": False,
            "context": """{
                'search_default_product_tmpl_id': [active_id],
                'default_product_tmpl_id': active_id, 'create': False
            }""",
        }
    )
