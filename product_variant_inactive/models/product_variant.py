# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    combination_deleted = fields.Boolean(
        help="If tick then this combination of variant"
        " has been deleted and can not be reactivated"
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="tree", toolbar=False, submenu=False
    ):
        """Dynamic modification of fields"""
        res = super(ProductProduct, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        root = etree.fromstring(res["arch"])
        if view_type == "tree":
            for button in root.findall(".//button"):
                if "search_disable_custom_filters" in self.env.context:
                    button.set("invisible", "0")
                    modifiers = json.loads(button.get("modifiers"))
                    modifiers["invisible"] = True
                    button.set("modifiers", json.dumps(modifiers))
            res["arch"] = etree.tostring(root, pretty_print=True)
        return res

    def write(self, vals):
        if vals.get("active") and self._context.get("unset_combination_deleted"):
            vals["combination_deleted"] = False
        for product in self:
            if (
                self._context.get("skip_reactivate_variant")
                and vals.get("active", False)
                and not product.active
                and not product.combination_deleted
            ):
                _logger.info("Skip reactivating product %s" % product.id)
            else:
                super(ProductProduct, product).write(vals)
        return True

    def _unlink_or_archive(self, check_access=True):
        records = self
        if not self._context.get("skip_filter_deleted"):
            records = records.filtered(
                lambda p: not p.combination_deleted
            ).with_context(skip_filter_deleted=True)
            records.write({"combination_deleted": True, "active": False})
        super(ProductProduct, records)._unlink_or_archive(check_access=check_access)

    @api.constrains("active", "combination_deleted")
    def _check_can_not_be_reativated(self):
        for record in self:
            if record.active and record.combination_deleted:
                raise UserError(
                    _(
                        "You cannot activate the product because this "
                        "combination has been deleted"
                    )
                )

    def unlink(self):
        # Pass active_test = False to avoid deleting template
        # with inactive variant
        return super(ProductProduct, self.with_context(active_test=False)).unlink()
