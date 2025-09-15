##############################################################################
# Copyright (c) 2025 braintec AG (https://braintec.com)
# All Rights Reserved
#
# Licensed under the AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
# See LICENSE file for full licensing details.
##############################################################################

from odoo import api, models
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        """Override to add warning from variant level."""
        res = super()._onchange_product_id_warning()
        if res:
            return res

        if not self.product_id:
            return

        product = self.product_id
        if product.variant_sale_line_warn != "no-message":
            if product.variant_sale_line_warn == "block":
                self.product_id = False

            return {
                "warning": {
                    "title": _("Warning for %s", product.name),
                    "message": product.variant_sale_line_warn_msg,
                }
            }

    def _get_product_catalog_lines_data(self, **kwargs):
        """Override to add warning from variant level."""
        res = super()._get_product_catalog_lines_data(**kwargs)
        if len(self) == 1:
            if not res["readOnly"]:
                res["readOnly"] |= self.product_id.variant_sale_line_warn == "block"
            if (
                self.product_id.variant_sale_line_warn != "no-message"
                and self.product_id.variant_sale_line_warn_msg
            ):
                res["warning"] = self.product_id.variant_sale_line_warn_msg
        elif self:
            if (
                self.product_id.variant_sale_line_warn != "no-message"
                and self.product_id.variant_sale_line_warn_msg
            ):
                res["warning"] = self.product_id.variant_sale_line_warn_msg

        return res
