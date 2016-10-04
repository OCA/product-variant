# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Variant Configurator',
    'summary': """
        Provides an abstract model for product variant configuration.""",
    'version': '9.0.1.0.0',
    'category': 'Product Variant',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,'
              'OdooMRP team,'
              'AvanzOSC,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': 'https://odoo-community.org/',
    'depends': [
        "product",
    ],
    'data': [
        'security/product_configurator_attribute.xml',
        'views/product_configurator_attribute.xml',
        'views/product_attribute_price.xml',
        'views/product_template.xml',
        'views/product_product.xml',
        'security/res_groups.xml',
        'views/product_category.xml',
    ],
}
