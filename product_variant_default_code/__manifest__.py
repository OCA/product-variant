# Copyright 2014 AvancOSC - Alfredo de la Fuente
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2014 Shine IT - Tony Gu
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Akretion - David Beal
# Copyright 2018 AvancOSC - Daniel Campos
# Copyright 2020 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Variant Default Code",
    "version": "13.0.1.1.0",
    "author": "AvancOSC," "Shine IT," "Tecnativa," "Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "category": "Product",
    "depends": ["product"],
    "data": [
        "security/product_security.xml",
        "data/ir_config_parameter.xml",
        "views/product_attribute_view.xml",
        "views/product_view.xml",
        "views/config_settings_view.xml",
    ],
    "demo": ["demo/attribute_demo.xml"],
    "installable": True,
}
