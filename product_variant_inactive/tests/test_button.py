# © 2017 Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.tests.common import SavepointCase


class TestProductProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.product_product_4 = cls.env.ref("product.product_product_4")

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

    def test_reactive_template(self):
        template = self.env["product.template"].create(
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
        variants = template.product_variant_ids
        template.write({"active": False})
        self.assertEqual(variants.mapped("active"), [False, False])
        template.write({"active": True})
        self.assertEqual(variants.mapped("active"), [True, True])

    def _deactivate_all_variants_of_template(self):
        self.template.product_variant_ids.write({"active": False})

    def test_template_after_deactivate_all_variants(self):
        self._deactivate_all_variants_of_template()
        self.assertFalse(self.template.active)

    def test_template_after_reactivate_one_variant(self):
        self._deactivate_all_variants_of_template()
        self.product_product_4.active = True
        self.assertTrue(self.template.active)
