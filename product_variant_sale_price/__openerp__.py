# -*- coding: utf-8 -*-
# (c) 2015 Incaser Informatica S.L. - Sergio Teruel
# (c) 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Product Variant Sale Price',
    'summary': 'Allow write fixed prices in product variants',
    'version': '8.0.1.0.0',
    'category': 'Portal',
    "website": "https://odoo-community.org/",
    'author': 'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product",
    ],
    'data': [
        'views/product_template_view.xml',
     ],
}
