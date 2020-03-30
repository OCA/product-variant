# Copyright 2020 Druidoo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, SUPERUSER_ID


def set_sale_description_on_variant(cr, registry):
    '''
    Hook on module install
    Copy the sale_description in the templates
    to the variants.
    '''
    cr.execute("""
        UPDATE product_product pp
        SET description_sale = pt.description_sale
        FROM product_template pt
        WHERE pt.id = pp.product_tmpl_id
    """)


def set_sale_description_on_template(cr, registry):
    '''
    Hook on module uninstall.
    In order to avoid data-loss, we copy the descriptions
    from the variants into the template.
    If they're different, we concatenate them with newlines
    '''
    env = api.Environment(cr, SUPERUSER_ID, {})
    products = env['product.template'].search([])
    for product in products:
        desc = False
        descriptions = product.product_variant_ids.mapped('description_sale')
        if not descriptions:
            continue
        if all(x == descriptions[0] for x in descriptions):
            desc = descriptions[0]
        else:
            desc = '\n\n'.join(descriptions)
        # We use sql so that it doesn't go through the inverse method
        if desc:
            cr.execute("""
                UPDATE product_template pt
                SET description_sale = %s
                WHERE pt.id = %s
            """, (desc, product.id))
