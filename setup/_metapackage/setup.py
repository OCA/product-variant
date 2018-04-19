import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-product_variant_configurator',
        'odoo10-addon-product_variant_default_code',
        'odoo10-addon-product_variant_supplierinfo',
        'odoo10-addon-product_variant_template_data',
        'odoo10-addon-purchase_order_variant_mgmt',
        'odoo10-addon-purchase_variant_configurator',
        'odoo10-addon-purchase_variant_configurator_on_confirm',
        'odoo10-addon-sale_order_line_variant_description',
        'odoo10-addon-sale_order_variant_mgmt',
        'odoo10-addon-sale_stock_variant_configurator',
        'odoo10-addon-sale_variant_configurator',
        'odoo10-addon-stock_picking_variant_mgmt',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
