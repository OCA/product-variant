import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-product_variant_attribute_tax',
        'odoo13-addon-product_variant_configurator',
        'odoo13-addon-product_variant_default_code',
        'odoo13-addon-product_variant_sale_price',
        'odoo13-addon-purchase_variant_configurator',
        'odoo13-addon-purchase_variant_configurator_on_confirm',
        'odoo13-addon-sale_product_variant_attribute_tax',
        'odoo13-addon-sale_variant_configurator',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
