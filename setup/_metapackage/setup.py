import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-product_variant_attribute_tax>=16.0dev,<16.1dev',
        'odoo-addon-product_variant_configurator>=16.0dev,<16.1dev',
        'odoo-addon-product_variant_default_code>=16.0dev,<16.1dev',
        'odoo-addon-product_variant_name>=16.0dev,<16.1dev',
        'odoo-addon-product_variant_sale_price>=16.0dev,<16.1dev',
        'odoo-addon-product_variant_specific_description>=16.0dev,<16.1dev',
        'odoo-addon-sale_order_line_variant_description>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
