# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Variant Configurator On Confirm',
    'summary': """
        Create product variants when confirming the purchase order""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    'website': 'https://odoo-community.org/',
    'depends': [
        'purchase_variant_configurator',
    ],
    'data': [
        "views/inherited_purchase_order_views.xml",
    ],
    'demo': [
    ],
}
