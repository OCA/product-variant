##############################################################################
# Copyright (c) 2025 braintec AG (https://braintec.com)
# All Rights Reserved
#
# Licensed under the AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
# See LICENSE file for full licensing details.
##############################################################################

from odoo import fields, models

from odoo.addons.base.models.res_partner import WARNING_HELP, WARNING_MESSAGE


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_sale_line_warn = fields.Selection(
        WARNING_MESSAGE,
        string="Variant Sales Order Line",
        help=WARNING_HELP,
        required=True,
        default="no-message",
    )
    variant_sale_line_warn_msg = fields.Text(
        string="Variant Message for Sales Order Line",
    )
