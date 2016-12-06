# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Invoice Product Variant Configurator',
    'summary': """
        Product variant configurator on invoice lines""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu/',
    'depends': [
        'account',
        'product_variant_configurator',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/account_invoice_line.xml',
    ],
    'demo': [
    ],
}
