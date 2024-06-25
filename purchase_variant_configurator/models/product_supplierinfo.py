# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """HACK: With NewId, the linked product_tmpl_id won't be a proper interger
        that we can use in a search. As we need it to get the proper pricelists
        we'll be passing it by context. The propper solution would be to
        use `self.product_tmpl_id._origin.id` in `_prepare_sellers`:
        https://github.com/odoo/odoo/blob/13.0/addons/product/models/product.py#L588"""
        if self.env.context.get("pvc_product_tmpl"):
            args2 = []
            for arg in args:
                if (
                    len(arg) == 3
                    and arg[0] == "product_tmpl_id"
                    and arg[1] == "="
                    and not isinstance(arg[2], int)
                ):
                    arg = (
                        "product_tmpl_id",
                        "=",
                        self.env.context.get("pvc_product_tmpl"),
                    )
                args2.append(arg)
            return super().search(
                args2, offset=offset, limit=limit, order=order, count=count
            )
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )
