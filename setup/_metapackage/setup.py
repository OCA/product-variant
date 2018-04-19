import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_invoice_variant_configurator',
        'odoo9-addon-product_variant_configurator',
        'odoo9-addon-product_variant_supplierinfo',
        'odoo9-addon-purchase_variant_configurator',
        'odoo9-addon-purchase_variant_configurator_on_confirm',
        'odoo9-addon-stock_picking_variant_mgmt',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
