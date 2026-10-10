# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import tagged

from odoo.addons.product_variant_change_template.tests.common import (
    ProductVariantChangeTemplateCommon,
)


@tagged("post_install", "-at_install")
class TestProductVariantChangeTemplateWebsiteSale(ProductVariantChangeTemplateCommon):
    def _move_into_shirt(self, policy):
        target = self._create_template("Shirt", {self.size: ["M"]})
        source = self._create_template("Shirt L", is_published=True)
        source_url, target_url = source.website_url, target.website_url
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.source_template_policy = policy
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        wizard_form.save().action_move()
        return self.env["website.rewrite"].search(
            [("url_from", "=", source_url), ("url_to", "=", target_url)]
        )

    def test_archived_source_is_redirected(self):
        rewrite = self._move_into_shirt("archive")
        self.assertEqual(rewrite.redirect_type, "301")

    def test_merged_source_is_redirected(self):
        rewrite = self._move_into_shirt("merge")
        self.assertEqual(rewrite.redirect_type, "301")

    def test_partial_move_keeps_source_page(self):
        source = self._create_template("Shirt", {self.size: ["M", "L"]})
        target = self._create_template("Premium shirt", {self.size: ["XL"]})
        wizard_form = self._open_wizard(self._variant(source, "L"))
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        self.assertFalse(
            self.env["website.rewrite"].search([("url_from", "=", source.website_url)])
        )
