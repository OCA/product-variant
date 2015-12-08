# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# © 2015 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Product Variant Cost Price",
    "summary": "Cost price by variant",
    "version": "8.0.1.0.0",
    "category": "Product Management",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/product-variant",
    "contributors": [
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Javier Iniesta <javieria@antiun.com>",
    ],
    "depends": [
        "product",
        "stock_account",
    ],
    "data": [
        'data/product_product_data.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "post_init_hook": "load_cost_price_on_variant",
}
