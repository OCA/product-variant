import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-product_variant_available_in_pos',
        'odoo11-addon-product_variant_configurator',
        'odoo11-addon-product_variant_default_code',
        'odoo11-addon-product_variant_sale_price',
        'odoo11-addon-purchase_variant_configurator',
        'odoo11-addon-purchase_variant_configurator_on_confirm',
        'odoo11-addon-sale_order_variant_mgmt',
        'odoo11-addon-sale_variant_configurator',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
