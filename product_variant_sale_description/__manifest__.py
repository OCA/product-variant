# Copyright 2020 Druidoo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Product Variant Sale Description',
    'summary': 'Allows to set description of product based on the variants.',
    'version': '12.0.1.0.0',
    'category': 'Product Management',
    'website': 'https://github.com/OCA/product-variant',
    'author': 'Druidoo, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'product',
        'sale_management'
    ],
    'data': [
        'views/product_views.xml',
    ],
    'post_init_hook': 'set_sale_description_on_variant',
    'uninstall_hook': 'set_sale_description_on_template',
}
