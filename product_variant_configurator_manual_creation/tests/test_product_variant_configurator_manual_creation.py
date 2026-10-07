# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import Form
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
        cls.attribute2 = cls.product_attribute.create({"name": "Test Attribute 2"})
        # Instances: product attribute value
        cls.value2_1 = cls.product_attribute_value.create(
            {"name": "Value 1 attribute 2", "attribute_id": cls.attribute2.id}
        )
        cls.value2_2 = cls.product_attribute_value.create(
            {"name": "Value 2 attribute 2", "attribute_id": cls.attribute2.id}
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
        self.assertTrue(self.product_template1.has_pending_variants)
        variant_creation_wizard1 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id, active_model="product.template"
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
        self.assertEqual(variant_creation_wizard1.variants_to_create, 1)
        variant_creation_wizard1.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 1)
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.id,
            self.value1.id,
        )

        variant_creation_wizard2 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id, active_model="product.template"
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
        self.assertEqual(variant_creation_wizard1.variants_to_create, 1)
        variant_creation_wizard2.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 2)
        variants = self.product_template1.product_variant_ids
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.ids,
            [self.value1.id, self.value2.id],
        )
        self.assertFalse(self.product_template1.has_pending_variants)
        # Archive second variant and call the wizard to "recreate" the variant,
        # in fact unarchive it
        snd_variant = variants[1]
        snd_variant.active = False
        variant_creation_wizard3 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id, active_model="product.template"
        ).create({})
        variant_creation_wizard3._onchange_product_tmpl()
        self.assertEqual(
            variant_creation_wizard3.line_ids.attribute_id.id, self.attribute1.id
        )
        variant_creation_wizard3.line_ids.write(
            {
                "selected_value_ids": [(6, 0, [self.value2.id])],
                "attribute_value_ids": [(6, 0, [self.value2.id])],
            }
        )
        self.assertEqual(variant_creation_wizard1.variants_to_create, 1)
        variant_creation_wizard2.action_create_variants()
        self.assertTrue(snd_variant.active)

    def test_product_attribute_manual_creation_from_variant(self):
        """
        Simulate the use of the wizard from a product.product
        """
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
        self.assertTrue(self.product_template1.has_pending_variants)
        variant_creation_wizard1 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id, active_model="product.template"
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
        self.assertEqual(variant_creation_wizard1.variants_to_create, 1)
        variant_creation_wizard1.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 1)
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.id,
            self.value1.id,
        )

        variant_creation_wizard2 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.product_variant_ids.id,
            active_model="product.product",
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
        self.assertEqual(variant_creation_wizard1.variants_to_create, 1)
        variant_creation_wizard2.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 2)
        variants = self.product_template1.product_variant_ids
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.ids,
            [self.value1.id, self.value2.id],
        )
        self.assertFalse(self.product_template1.has_pending_variants)

    def test_product_attribute_manual_creation_invalid_combination(self):
        """
        Try to create a variant for a forbidden combination
        """
        self.product_template1 = self.product_template.create(
            {"name": "Product template 1", "no_create_variants": "yes"}
        )
        self.assertEqual(self.product_template1.product_variant_count, 1)
        variants = self.product_template1.product_variant_ids
        self.assertEqual(
            variants.product_template_attribute_value_ids.product_attribute_value_id.id,
            False,
        )
        # Configure the attributes on the product
        self.attribute_line_model.with_context(check_variant_creation=True).create(
            [
                {
                    "product_tmpl_id": self.product_template1.id,
                    "attribute_id": self.attribute1.id,
                    "value_ids": [(6, 0, [self.value1.id, self.value2.id])],
                },
                {
                    "product_tmpl_id": self.product_template1.id,
                    "attribute_id": self.attribute2.id,
                    "value_ids": [(6, 0, [self.value2_1.id, self.value2_2.id])],
                },
            ]
        )
        self.assertTrue(self.product_template1.has_pending_variants)

        # Create all the variants with the wizard
        variant_creation_wizard1 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id, active_model="product.template"
        ).create({})
        variant_creation_wizard1._onchange_product_tmpl()
        self.assertEqual(
            variant_creation_wizard1.line_ids.mapped("attribute_id"),
            self.attribute1 | self.attribute2,
        )
        variant_creation_wizard1.line_ids.filtered(
            lambda line: line.attribute_id == self.attribute1
        ).write(
            {
                "selected_value_ids": [(6, 0, [self.value1.id, self.value2.id])],
                "attribute_value_ids": [(6, 0, [self.value1.id, self.value2.id])],
            }
        )
        variant_creation_wizard1.line_ids.filtered(
            lambda line: line.attribute_id == self.attribute2
        ).write(
            {
                "selected_value_ids": [(6, 0, [self.value2_1.id, self.value2_2.id])],
                "attribute_value_ids": [(6, 0, [self.value2_1.id, self.value2_2.id])],
            }
        )
        self.assertEqual(variant_creation_wizard1.variants_to_create, 4)
        variant_creation_wizard1.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 4)
        # Add an exclusion for Product Template 1: Value 1 for attributes 1 and 2
        # cannot be set together
        template_variants = self.product_template1.product_variant_ids
        template_ptav = template_variants.product_template_attribute_value_ids
        ptav_attribute_1_value_1 = template_ptav.filtered(
            lambda ptav: ptav.attribute_id == self.attribute1
            and ptav.product_attribute_value_id == self.value1
        )
        ptav_attribute_2_value_1 = template_ptav.filtered(
            lambda ptav: ptav.attribute_id == self.attribute2
            and ptav.product_attribute_value_id == self.value2_1
        )
        self.env["product.template.attribute.exclusion"].create(
            {
                "product_template_attribute_value_id": ptav_attribute_1_value_1.id,
                "product_tmpl_id": self.product_template1.id,
                "value_ids": [(6, 0, [ptav_attribute_2_value_1.id])],
            }
        )
        # Unwanted variant has been deleted
        self.assertEqual(self.product_template1.product_variant_count, 3)
        # Try to re-create it using the wizard
        variant_creation_wizard2 = self.wizard_variant_manual_creation.with_context(
            active_id=self.product_template1.id, active_model="product.template"
        ).create({})
        variant_creation_wizard2._onchange_product_tmpl()
        variant_creation_wizard2.line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": self.attribute1.id,
                    "selected_value_ids": [(6, 0, [self.value1.id])],
                    "attribute_value_ids": [(6, 0, [self.value1.id])],
                },
            ),
            (
                0,
                0,
                {
                    "attribute_id": self.attribute2.id,
                    "selected_value_ids": [(6, 0, [self.value2_1.id])],
                    "attribute_value_ids": [(6, 0, [self.value2_1.id])],
                },
            ),
        ]
        variant_creation_wizard1.action_create_variants()
        self.assertEqual(self.product_template1.product_variant_count, 3)

    def _create_template_with_pending_variants(self, name):
        template = self.product_template.create(
            {"name": name, "no_create_variants": "yes"}
        )
        self.attribute_line_model.with_context(check_variant_creation=True).create(
            {
                "product_tmpl_id": template.id,
                "attribute_id": self.attribute1.id,
                "value_ids": [Command.set([self.value1.id, self.value2.id])],
            }
        )
        return template

    def test_pending_variants_several_templates(self):
        pending = self._create_template_with_pending_variants("Pending")
        complete = self.product_template.create({"name": "Without attributes"})
        templates = pending | complete
        templates.invalidate_recordset(["has_pending_variants"])
        self.assertEqual(templates.mapped("has_pending_variants"), [True, False])

    def test_pending_variants_form_with_exclusions(self):
        self.env.user.groups_id |= self.env.ref("product.group_product_variant")
        value3 = self.product_attribute_value.create(
            {"name": "Value 3", "attribute_id": self.attribute1.id}
        )
        template = self._create_template_with_pending_variants("With exclusions")
        self.attribute_line_model.with_context(check_variant_creation=True).create(
            {
                "product_tmpl_id": template.id,
                "attribute_id": self.attribute2.id,
                "value_ids": [Command.set([self.value2_1.id, self.value2_2.id])],
            }
        )
        values = template.attribute_line_ids.product_template_value_ids
        self.env["product.template.attribute.exclusion"].with_context(
            check_variant_creation=True
        ).create(
            {
                "product_tmpl_id": template.id,
                "product_template_attribute_value_id": values.filtered(
                    lambda v: v.product_attribute_value_id == self.value1
                ).id,
                "value_ids": [
                    Command.set(
                        values.filtered(
                            lambda v: v.product_attribute_value_id == self.value2_1
                        ).ids
                    )
                ],
            }
        )
        template_form = Form(template)
        self.assertTrue(template_form.has_pending_variants)
        # Editing the attributes recomputes the field on the unsaved record
        with self.assertNoLogs("odoo.models", level="WARNING"):
            with template_form.attribute_line_ids.edit(0) as line:
                line.value_ids.add(value3)
        self.assertTrue(template_form.has_pending_variants)
