# Copyright 2017 Jose Luis Sandoval Alaguna <jose.alaguna@rotafilo.com.tr>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

def assign_product_template(cr, registry):
    """This post-init-hook will update all existing mrp.bom.line"""
    cr.execute("""
        UPDATE mrp_bom_line AS line
        SET product_tmpl_id = product_product.product_tmpl_id
        FROM product_product
        WHERE line.product_id = product_product.id;""")
