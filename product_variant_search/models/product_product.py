# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    search_name = fields.Char(readonly=True, translate=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        variants = super().create(vals_list)
        variants.assign_search_name_all_langs()
        return variants

    def write(self, vals):
        res = super().write(vals)
        if "default_code" in vals:
            self.assign_search_name_all_langs()
        return res

    def assign_search_name_all_langs(self):
        langs = self.env["res.lang"].search([("active", "=", True)]).mapped("code")
        values = []
        for variant in self:
            data = {
                lang: variant.with_context(lang=lang).display_name for lang in langs
            }
            values.append((variant.id, json.dumps(data)))
        self.env.cr.execute_values(
            """
            UPDATE product_product AS p
            SET search_name = v.search_name::jsonb
            FROM (VALUES %s) AS v(id, search_name)
            WHERE p.id = v.id
            """,
            values,
            template="(%s, %s)",
        )
        self.invalidate_recordset(["search_name"])
        return

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        if not name:
            return super().name_search(name, args, operator, limit)
        res = super().name_search(name, args, operator, limit)
        if limit and len(res) >= limit:
            return res
        found_ids = [pid for pid, _ in res]
        limit_rest = (limit - len(res)) if limit else None
        extra_domain = expression.AND(
            [
                args,
                [("id", "not in", found_ids)],
                [("search_name", operator, name)],
            ]
        )
        extra = self.search_fetch(extra_domain, ["display_name"], limit=limit_rest)
        return res + [(p.id, p.display_name) for p in extra.sudo()]

    @api.model
    def _cron_populate_search_name(self, batch_size=2000):
        Product = self.env["product.product"]
        domain = [("search_name", "=", False)]
        recs = Product.search(domain, limit=batch_size)
        if not recs:
            return
        recs.assign_search_name_all_langs()
        if Product.search(domain, limit=1):
            self.env.ref(
                "product_variant_search.ir_cron_populate_search_name"
            )._trigger()
