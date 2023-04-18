# © 2017 Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestProductProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.product_product_4 = cls.env.ref("product.product_product_4")
        cls.product_product_4c = cls.env.ref("product.product_product_4c")

    def test_fields_view_get_tree(self):
        product = self.help_create_product()
        product = product.with_context({"search_disable_custom_filters": True})
        root = etree.fromstring(product.fields_view_get()["arch"])
        for button in root.findall(".//button"):
            self.assertEqual("0", button.get("invisible", "0"))

    def test_fields_view_get_form(self):
        # button should appear if we have only 1 active product,
        # and n other inactive products
        product_template = self.env["product.template"].create(
            {"name": "product template with two variants"}
        )
        self.env["product.product"].create(
            {
                "name": "active product",
                "product_tmpl_id": product_template.id,
                "active": True,
            }
        )
        self.env["product.product"].create(
            {
                "name": "inactive product",
                "product_tmpl_id": product_template.id,
                "active": False,
            }
        )
        button_action_ref = self.env.ref("product.product_variant_action").id
        root = etree.fromstring(product_template.fields_view_get()["arch"])
        button = root.findall(".//button[@name='%d']" % button_action_ref)[0]
        self.assertEqual("0", button.get("invisible", "0"))

    def help_create_product(self, active=True):
        product = self.env["product.product"].create(
            {"active": active, "name": "test_product"}
        )
        return product

    def test_create_variant_do_not_reactivate(self):
        """Ensure that re-generating variants does not
        change the "active" state of the existing variant"""
        self.product_product_4.active = False
        self.product_product_4.product_tmpl_id._create_variant_ids()
        self.assertFalse(self.product_product_4.active)

    def test_product_variant_count(self):
        self.product_product_4.active = False
        variant_count = self.template.product_variant_count
        variant_count_all = self.template.product_variant_count_all
        self.product_product_4.active = True
        self.assertEqual(self.template.product_variant_count, variant_count + 1)
        self.assertEqual(self.template.product_variant_count_all, variant_count_all)

    def _create_template_with_variant(self):
        return self.env["product.template"].create(
            {
                "name": "FOO",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.env.ref(
                                "product.product_attribute_2"
                            ).id,
                            "value_ids": [
                                self.env.ref("product.product_attribute_value_3").id,
                                self.env.ref("product.product_attribute_value_4").id,
                            ],
                        },
                    )
                ],
            }
        )

    def test_reactive_template(self):
        template = self._create_template_with_variant()
        variants = template.product_variant_ids
        template.write({"active": False})
        self.assertEqual(variants.mapped("active"), [False, False])
        template.write({"active": True})
        self.assertEqual(variants.mapped("active"), [True, True])

    def test_unlink_variant_with_archive_template(self):
        template = self._create_template_with_variant()
        variant = template.product_variant_ids[0]
        template.active = False
        variant.unlink()
        self.assertTrue(template.exists())

    def _deactivate_all_variants_of_template(self):
        self.template.product_variant_ids.write({"active": False})

    def test_template_after_deactivate_all_variants(self):
        self._deactivate_all_variants_of_template()
        self.assertFalse(self.template.active)

    def test_template_after_reactivate_one_variant(self):
        self._deactivate_all_variants_of_template()
        self.product_product_4.active = True
        self.assertTrue(self.template.active)

    def _remove_combination(self):
        with mock.patch.object(
            type(self.env["product.product"]), "unlink", side_effect=UserError
        ):
            self.env.ref("product.product_4_attribute_2_value_1").unlink()

    def test_remove_combination(self):
        self._remove_combination()
        # check that variant is inactive and combination_deleted is True
        self.assertFalse(self.product_product_4c.active)
        self.assertTrue(self.product_product_4c.combination_deleted)

    def test_remove_combination_not_activable(self):
        self._remove_combination()
        with self.assertRaises(UserError):
            self.product_product_4c.active = True

    def test_reactive_combination(self):
        self._remove_combination()
        # reactive combination
        self.env.ref("product.product_4_attribute_2_value_1").ptav_active = True
        self.product_product_4c.product_tmpl_id._create_variant_ids()
        # check that variant is active and combination_deleted is False
        self.assertTrue(self.product_product_4c.active)
        self.assertFalse(self.product_product_4c.combination_deleted)
