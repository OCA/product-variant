import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-product-variant",
    description="Meta package for oca-product-variant Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-product_variant_default_code',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
