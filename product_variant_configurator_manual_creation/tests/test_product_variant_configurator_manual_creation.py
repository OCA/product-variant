# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductVariantConfiguratorManualCreation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ENVIRONMENTS
        cls.product_attribute = cls.env["product.attribute"]
        cls.product_attribute_value = cls.env["product.attribute.value"]
        cls.attribute_line_model = cls.env["product.template.attribute.line"]
        cls.wizard_variant_manual_creation = cls.env[
            "wizard.product.variant.configurator.manual.creation"
        ]
        cls.product_configuration_attribute = cls.env["product.configurator.attribute"]
        cls.product_template = cls.env["product.template"].with_context(
            check_variant_creation=True
        )
        # Instances: product attribute
        cls.attribute1 = cls.product_attribute.create({"name": "Test Attribute 1"})
        # Instances: product attribute value
        cls.value1 = cls.product_attribute_value.create(
            {"name": "Value 1", "attribute_id": cls.attribute1.id}
        )
        cls.value2 = cls.product_attribute_value.create(
            {"name": "Value 2", "attribute_id": cls.attribute1.id}
        )

    def test_product_attribute_manual_creation(self):
        # create product with attribute and "Variant creation" option is
        # set on "Don't create automatically"
        self.product_template1 = self.product_template.create(
            {"name": "Product template 1", "no_create_variants": "yes"}
        )
        self.attribute_line_model.with_context(check_variant_creation=True).create(
            {
                "product_tmpl_id": self.product_template1.id,
                "attribute_id": self.attribute1.id,
                "value_ids": [(6, 0, [self.value1.id, self.value2.id])],
            }
        )
        self.assertEqual(self.product_template1.product_variant_count, 1)
        variants = self.product_template1.product_variant_ids
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.id,
            False,
        )
        variant_creation_wizard1 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id
        ).create({})
        variant_creation_wizard1._onchange_product_tmpl()
        self.assertEqual(
            variant_creation_wizard1.line_ids.attribute_id.id, self.attribute1.id
        )
        variant_creation_wizard1.line_ids.write(
            {
                "selected_value_ids": [(6, 0, [self.value1.id])],
                "attribute_value_ids": [(6, 0, [self.value1.id])],
            }
        )
        variant_creation_wizard1.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 1)
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.id,
            self.value1.id,
        )

        variant_creation_wizard2 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id
        ).create({})
        variant_creation_wizard2._onchange_product_tmpl()
        self.assertEqual(
            variant_creation_wizard2.line_ids.attribute_id.id, self.attribute1.id
        )
        variant_creation_wizard2.line_ids.write(
            {
                "selected_value_ids": [(6, 0, [self.value2.id])],
                "attribute_value_ids": [(6, 0, [self.value2.id])],
            }
        )
        variant_creation_wizard2.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 2)
        variants = self.product_template1.product_variant_ids
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.ids,
            [self.value1.id, self.value2.id],
        )
