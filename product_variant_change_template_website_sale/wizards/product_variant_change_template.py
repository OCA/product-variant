# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models


class ProductVariantChangeTemplate(models.TransientModel):
    _inherit = "product.variant.change.template"

    def _prepare_source_removal(self, source):
        """The shop page of an archived or deleted template answers 404; send
        its visitors and search engines to the target instead."""
        res = super()._prepare_source_removal(source)
        target = self.target_tmpl_id
        if source.website_url and target.website_url:
            self.env["website.rewrite"].sudo().create(
                {
                    "name": _("Moved product: %(name)s", name=source.display_name),
                    "redirect_type": "301",
                    "url_from": source.website_url,
                    "url_to": target.website_url,
                    "website_id": source.website_id.id,
                }
            )
        return res
