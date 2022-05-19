import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-product_matrix_show_color',
        'odoo14-addon-product_variant_default_code',
        'odoo14-addon-product_variant_inactive',
        'odoo14-addon-product_variant_sale_price',
        'odoo14-addon-sale_order_line_variant_description',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
