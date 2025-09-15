##############################################################################
# Copyright (c) 2025 braintec AG (https://braintec.com)
# All Rights Reserved
#
# Licensed under the AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
# See LICENSE file for full licensing details.
##############################################################################
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_product_catalog_order_data(self, products, **kwargs):
        res = super()._get_product_catalog_order_data(products, **kwargs)
        for product in products:
            if (
                product.variant_sale_line_warn != "no-message"
                and product.variant_sale_line_warn_msg
            ):
                res[product.id]["warning"] = product.variant_sale_line_warn_msg
            if product.variant_sale_line_warn == "block":
                res[product.id]["readOnly"] = True
        return res
