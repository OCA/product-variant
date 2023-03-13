# Copyright 2017 Tecnativa - David Vidal
# Copyright 2020-2021 Tecnativa - João Marques
# Copyright 2021 Akretion - Kévin Roche
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestVariantDefaultCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestVariantDefaultCode, cls).setUpClass()
        cls.group_default_code = cls.env.ref(
            "product_variant_default_code.group_product_default_code_manual_mask"
        )
        cls.attr1 = cls.env["product.attribute"].create(
            {
                "name": "TSize",
                "sequence": 0,
            }
        )
        cls.attr2 = cls.env["product.attribute"].create(
            {
                "name": "TColor",
                "sequence": 1,
            }
        )
        cls.attr1_1 = cls.env["product.attribute.value"].create(
            {"name": "L", "attribute_id": cls.attr1.id}
        )
        cls.attr1_2 = cls.env["product.attribute.value"].create(
            {"name": "XL", "attribute_id": cls.attr1.id}
        )
        cls.attr2_1 = cls.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": cls.attr2.id}
        )
        cls.attr2_2 = cls.env["product.attribute.value"].create(
            {"name": "Green", "attribute_id": cls.attr2.id}
        )
        cls.template1 = cls.env["product.template"].create(
            {
                "name": "Jacket",
                "code_prefix": "prefix/",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr1.id,
                            "value_ids": [(6, 0, [cls.attr1_1.id, cls.attr1_2.id])],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr2.id,
                            "value_ids": [(6, 0, [cls.attr2_1.id, cls.attr2_2.id])],
                        },
                    ),
                ],
            }
        )

    def test_01_check_default_codes(self):
        # As no mask was set, a default one should be:
        self.assertEqual(self.template1.reference_mask, "prefix/[TSize]-[TColor]")
        # Check that variants code are generated according to rules
        for product in self.template1.mapped("product_variant_ids"):
            expected_code = (
                self.template1.code_prefix
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
                + "-"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)

    def test_02_check_default_codes_preexistent_mask(self):
        self.env.user.groups_id |= self.group_default_code
        # Second template with custom reference mask must be created with correct
        # user permissions
        template2 = self.template1.copy(
            {
                "name": "Pants",
                "reference_mask": "P01/[TSize][TColor]",
            }
        )
        for product in template2.mapped("product_variant_ids"):
            expected_code = (
                "P01/"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)

    def test_03_reset_reference_mask_to_default(self):
        # Erase the previous mask: 'P01/[TSize][TColor]'
        self.template1.reference_mask = ""
        # Mask is set to default now:
        self.assertEqual(self.template1.reference_mask, "prefix/[TSize]-[TColor]")

    def test_04_custom_reference_mask(self):
        self.env.user.groups_id |= self.group_default_code
        self.template1.reference_mask = "JKTÜ/[TColor]#[TSize]"
        for product in self.template1.mapped("product_variant_ids"):
            expected_code = (
                self.template1.code_prefix
                + "JKTÜ/"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
                + "#"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)

    def test_05_manual_code(self):
        self.env.user.groups_id |= self.group_default_code
        self.assertEqual(self.template1.product_variant_ids[0].manual_code, False)
        self.template1.product_variant_ids[0].default_code = "CANT-TOUCH-THIS"
        self.assertEqual(self.template1.product_variant_ids[0].manual_code, True)
        # Set a reference mask and check the other variants are changed
        self.template1.reference_mask = "J[TColor][TSize]"
        for product in self.template1.mapped("product_variant_ids")[1:]:
            expected_code = (
                self.template1.code_prefix
                + "J"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)
        # But this one isn't:
        self.assertEqual(
            self.template1.product_variant_ids[0].default_code, "CANT-TOUCH-THIS"
        )

    def test_06_attribute_value_code_change_propagation(self):
        self.attr1_1.code = "OO"
        # Check that the change spreads to every product
        products = self.env["product.product"].search(
            [
                (
                    "product_template_attribute_value_ids.product_attribute_value_id",
                    "=",
                    self.attr1_1.id,
                )
            ]
        )
        for product in products:
            self.assertTrue("OO" in product.default_code)

    def test_07_attribute_value_name_change(self):
        """Only set a default code if it wasn't set"""
        self.attr1_1.name = "New Name"
        self.assertEqual(self.attr1_1.code, "L")
        products = self.env["product.product"].search(
            [
                (
                    "product_template_attribute_value_ids.product_attribute_value_id",
                    "=",
                    self.attr1_1.id,
                )
            ]
        )
        # Check that the code persists
        for product in products:
            self.assertTrue("L" in product.default_code)
        # Otherwise, if there's no code a default value is set
        self.attr1_1.code = False
        self.attr1_1.name = "Odoo"
        self.assertEqual(self.attr1_1.code, "Od")
        for product in products:
            self.assertTrue("Od" in product.default_code)

    def test_08_sanitize_exception(self):
        self.env.user.groups_id |= self.group_default_code
        with self.assertRaises(UserError):
            self.env["product.template"].create(
                {
                    "name": "Shirt",
                    "attribute_line_ids": [
                        (
                            0,
                            0,
                            {
                                "attribute_id": self.attr1.id,
                                "value_ids": [(6, 0, [self.attr1_1.id])],
                            },
                        ),
                    ],
                    "reference_mask": "FAIL:[TSize][TWrongAttr]",
                }
            )

    def test_09_code_change_propagation(self):
        self.attr1.code = "AC"
        # Check that the change spreads to every product
        for product in (
            self.attr1.mapped("attribute_line_ids")
            .mapped("product_tmpl_id")
            .mapped("product_variant_ids")
        ):
            self.assertTrue("AC" in product.default_code)

        self.attr1_1.code = ":-)"
        self.assertTrue(":-)" in self.template1.product_variant_ids[0].default_code)

    def test_10_code_change_propagation_archived_variant(self):
        self.template1.product_variant_ids[0].active = False
        self.attr1.code = "o_o"
        self.assertTrue("o_o" in self.template1.product_variant_ids[0].default_code)
        self.attr1_1.code = "^_^"
        self.assertTrue("^_^" in self.template1.product_variant_ids[0].default_code)

    def test_11_prefix_code_as_default_code_by_default(self):
        self.assertFalse(self.template1.default_code)
        self.env["ir.config_parameter"].set_param("prefix_as_default_code", True)
        self.template1.code_prefix = "prefix_code"
        self.assertTrue(self.template1.default_code, self.template1.code_prefix)

    def test_12_prefix_change(self):
        for product in self.template1.mapped("product_variant_ids"):
            expected_code = (
                self.template1.code_prefix
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
                + "-"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)

    def test_13_new_attribute(self):
        self.assertEqual(self.template1.reference_mask, "prefix/[TSize]-[TColor]")
        self.assertEqual(len(self.template1.mapped("product_variant_ids")), 4)

        self.attr3 = self.env["product.attribute"].create({"name": "TCollection"})
        self.attr3_1 = self.env["product.attribute.value"].create(
            {"name": "New", "attribute_id": self.attr3.id}
        )
        self.attr3_2 = self.env["product.attribute.value"].create(
            {"name": "Old", "attribute_id": self.attr3.id}
        )

        self.template1.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attr3.id,
                            "value_ids": [(6, 0, [self.attr3_1.id, self.attr3_2.id])],
                        },
                    ),
                ]
            }
        )

        self.assertEqual(
            self.template1.reference_mask, "prefix/[TSize]-[TColor]-[TCollection]"
        )
        self.assertEqual(len(self.template1.mapped("product_variant_ids")), 8)

        for product in self.template1.mapped("product_variant_ids"):
            expected_code = (
                self.template1.code_prefix
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
                + "-"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
                + "-"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr3
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)

    def test_14_rename_attribute(self):
        self.assertEqual(self.template1.reference_mask, "prefix/[TSize]-[TColor]")
        self.attr1.name = "TNewSize"
        self.assertEqual(self.template1.reference_mask, "prefix/[TNewSize]-[TColor]")

    def test_15_sequence_change(self):
        self.assertEqual(self.template1.reference_mask, "prefix/[TSize]-[TColor]")
        self.attr1.sequence = 1
        self.attr2.sequence = 0
        self.template1.reference_mask = "prefix/[TColor]-[TSize]"
        self.template1.write({"name": "New"})
        self.assertEqual(self.template1.reference_mask, "prefix/[TColor]-[TSize]")

    def test_16_missing_prefix(self):
        self.template1.code_prefix = None
        for product in self.template1.mapped("product_variant_ids"):
            self.assertFalse(product.default_code)
        expected_error = (
            "Default Code can not be computed.\nReference Prefix is missing.\n"
        )
        self.assertEqual(self.template1.variant_default_code_error, expected_error)

    def test_17_missing_attribute_value_code(self):
        self.assertEqual(
            len(
                list(
                    filter(
                        None, self.template1.product_variant_ids.mapped("default_code")
                    )
                )
            ),
            4,
        )
        # 1 missing value code
        self.attr1_2.code = ""
        self.assertEqual(
            len(
                list(
                    filter(
                        None, self.template1.product_variant_ids.mapped("default_code")
                    )
                )
            ),
            2,
        )
        expected_error = "Default Code can not be computed.\n"
        expected_error += "Following attribute value have an empty code :\n"
        expected_error += "- XL"
        self.assertEqual(self.template1.variant_default_code_error, expected_error)
        # 2 missing value codes
        self.attr2_2.code = ""
        expected_error += "\n- Green"
        self.assertEqual(
            len(
                list(
                    filter(
                        None, self.template1.product_variant_ids.mapped("default_code")
                    )
                )
            ),
            1,
        )
        self.assertEqual(self.template1.variant_default_code_error, expected_error)

    def test_18_both_prefix_and_mask_changing(self):
        self.env.user.groups_id |= self.group_default_code
        self.template1.write(
            {
                "code_prefix": "pre/",
                "reference_mask": "fix-[TColor]/[TSize]",
            }
        )

        for product in self.template1.mapped("product_variant_ids"):
            expected_code = (
                self.template1.code_prefix
                + "fix-"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr2
                ).name[0:2]
                + "/"
                + product.product_template_attribute_value_ids.filtered(
                    lambda x: x.product_attribute_value_id.attribute_id == self.attr1
                ).name[0:2]
            )
            self.assertEqual(product.default_code, expected_code)
