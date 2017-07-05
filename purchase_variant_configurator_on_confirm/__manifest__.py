# -*- coding: utf-8 -*-
# Copyright 2016 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Purchase Variant Configurator On Confirm',
    'summary': """
        Create product variants when confirming the purchase order""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    "author": "AvanzOSC, "
              "Tecnativa, "
              "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    'website': 'https://odoo-community.org/',
    'depends': [
        'purchase_variant_configurator',
    ],
    'data': [
        "views/inherited_purchase_order_views.xml",
    ],
    'installable': True,
}
