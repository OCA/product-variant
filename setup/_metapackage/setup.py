import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-product_variant_available_in_pos',
        'odoo8-addon-product_variant_cost_price',
        'odoo8-addon-product_variant_csv_import',
        'odoo8-addon-product_variant_sale_delay',
        'odoo8-addon-product_variant_sale_price',
        'odoo8-addon-product_variant_search_by_attribute',
        'odoo8-addon-product_variant_storage_location',
        'odoo8-addon-product_variant_supplierinfo',
        'odoo8-addon-product_variant_uos',
        'odoo8-addon-product_variant_update_price',
        'odoo8-addon-product_variant_weight',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
