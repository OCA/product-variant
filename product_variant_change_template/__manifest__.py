{
    "name": "Product Variant Change Template",
    "version": "16.0.1.0.0",
    "summary": "Tool to allow change template of a existing product variant",
    "category": "Tools",
    "author": "ForgeFlow S.L, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "license": "AGPL-3",
    "depends": ["product_variant_configurator", "product_variant_sale_price"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_product_variant_change_template_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
    },
}
