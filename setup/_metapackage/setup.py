import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-product_variant_configurator',
        'odoo12-addon-product_variant_default_code',
        'odoo12-addon-product_variant_sale_price',
        'odoo12-addon-purchase_order_variant_mgmt',
        'odoo12-addon-sale_order_variant_mgmt',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
