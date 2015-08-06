# -*- coding: utf-8 -*-
#############################################################################
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#############################################################################

{
    "name": "Product variant automatic creation selectable",
    "summary": "Prevents the automatic creation of the variants of a product",
    "version": "8.0.1.0.0",
    "category": "Product Management",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "product",
    ],
    "data": [
        "views/product_view.xml",
    ],
    "installable": True,
}
