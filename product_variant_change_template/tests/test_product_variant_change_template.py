from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestProductVariantChangeTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard_model = cls.env["wizard.product.variant.change.template"]
        # ENVIRONMENTS
        cls.product_attribute = cls.env["product.attribute"]
        cls.product_attribute_value = cls.env["product.attribute.value"]
        cls.product_configurator_attribute = cls.env["product.configurator.attribute"]
        cls.product_category = cls.env["product.category"]
        cls.product_product = cls.env["product.product"]
        cls.product_template = cls.env["product.template"].with_context(
            check_variant_creation=True
        )

        # Instances: product attribute
        cls.attribute1 = cls.product_attribute.create({"name": "Test Attribute 1"})
        cls.attribute2 = cls.product_attribute.create({"name": "Test Attribute 2"})
        # Instances: product attribute value
        cls.value1 = cls.product_attribute_value.create(
            {"name": "Value 1", "attribute_id": cls.attribute1.id}
        )
        cls.value2 = cls.product_attribute_value.create(
            {"name": "Value 2", "attribute_id": cls.attribute1.id}
        )
        cls.value3 = cls.product_attribute_value.create(
            {"name": "Value 3", "attribute_id": cls.attribute2.id}
        )
        cls.value4 = cls.product_attribute_value.create(
            {"name": "Value 4", "attribute_id": cls.attribute2.id}
        )
        cls.price_list = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist Test",
            }
        )

        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier",
            }
        )

    def test_01_update_template(self):
        tmpl = self.product_template.with_context(
            product_name="No create variants template"
        ).create(
            {
                "name": "No create variants template",
                "no_create_variants": "yes",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute1.id,
                            "value_ids": [(6, 0, [self.value1.id, self.value2.id])],
                            "required": True,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute2.id,
                            "value_ids": [(6, 0, [self.value3.id, self.value4.id])],
                        },
                    ),
                ],
            }
        )
        self.assertEqual(len(tmpl.product_variant_ids), 0)

        product_1 = (
            self.env["product.product"]
            .with_context(product_name="Product 1")
            .create({"name": "Product 1", "lst_price": 100.0})
        )
        product_tmpl_1 = product_1.product_tmpl_id
        self.price_list_item = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.price_list.id,
                "applied_on": "1_product",
                "product_tmpl_id": product_tmpl_1.id,
                "fixed_price": 100.0,
            }
        )
        product_tmpl_1.write(
            {
                "seller_ids": [
                    (0, 0, {"delay": 1, "partner_id": self.supplier.id, "min_qty": 2.0})
                ]
            }
        )

        product_2 = (
            self.env["product.product"]
            .with_context(product_name="Product 2")
            .create({"name": "Product 2", "lst_price": 150.0})
        )
        product_tmpl_2 = product_2.product_tmpl_id
        self.price_list_item = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.price_list.id,
                "applied_on": "1_product",
                "product_tmpl_id": product_tmpl_2.id,
                "fixed_price": 150.0,
            }
        )
        product_3 = (
            self.env["product.product"]
            .with_context(product_name="Product 3")
            .create({"name": "Product 3", "lst_price": 130.0})
        )
        product_tmpl_3 = product_3.product_tmpl_id
        product_4 = (
            self.env["product.product"]
            .with_context(product_name="Product 4")
            .create({"name": "Product 4", "lst_price": 180.0})
        )
        product_tmpl_4 = product_4.product_tmpl_id
        product_5 = (
            self.env["product.product"]
            .with_context(product_name="Product 5")
            .create(
                {
                    "name": "Product 5",
                    "lst_price": 200.0,
                    "uom_id": self.env.ref("uom.product_uom_meter").id,
                    "uom_po_id": self.env.ref("uom.product_uom_meter").id,
                }
            )
        )

        # Associate product 1
        wizard_form = Form(
            self.wizard_model.with_context(
                active_model="product.product", active_id=product_1.id
            )
        )

        # Should be shown all values of product template
        wizard_form.destination_template_id = tmpl
        wizard = wizard_form.save()
        self.assertEqual(
            wizard.available_value_ids.ids,
            [self.value1.id, self.value2.id, self.value3.id, self.value4.id],
        )

        wizard_form = Form(
            wizard.with_context(active_model="product.product", active_id=product_1.id)
        )

        # When a value is selected then should be removed all values associated to its attribute
        wizard_form.selected_value_ids.add(self.value1)
        wizard = wizard_form.save()
        self.assertEqual(
            wizard.available_value_ids.ids, [self.value3.id, self.value4.id]
        )

        wizard_form = Form(
            wizard.with_context(active_model="product.product", active_id=product_1.id)
        )

        # When a value is selected then should be removed all values associated to its attribute
        wizard_form.selected_value_ids.add(self.value3)
        wizard = wizard_form.save()
        self.assertEqual(wizard.available_value_ids.ids, [])

        wizard.action_change_template()

        self.assertEqual(product_1.product_tmpl_id, tmpl)
        self.assertEqual(product_1.lst_price, 100.0)
        self.assertFalse(product_tmpl_1.active)
        self.assertEqual(tmpl.pricelist_item_count, 1)
        self.assertEqual(len(tmpl.seller_ids), 1)

        # Associate product 2
        wizard_form = Form(
            self.wizard_model.with_context(
                active_model="product.product", active_id=product_2.id
            )
        )
        wizard_form.destination_template_id = tmpl
        wizard_form.selected_value_ids.add(self.value1)
        wizard_form.selected_value_ids.add(self.value3)

        # With select combination of values should be added as an existing variant
        wizard = wizard_form.save()
        self.assertTrue(bool(wizard.already_exist_variant_ids))

        wizard_form = Form(
            wizard.with_context(active_model="product.product", active_id=product_2.id)
        )
        wizard_form.selected_value_ids.remove(self.value3.id)
        wizard_form.selected_value_ids.add(self.value4)
        wizard = wizard_form.save()
        wizard.action_change_template()

        self.assertEqual(product_2.product_tmpl_id, tmpl)
        self.assertEqual(product_1.lst_price, 100.0)
        self.assertEqual(product_2.lst_price, 150.0)
        self.assertFalse(product_tmpl_2.active)
        self.assertEqual(tmpl.pricelist_item_count, 2)

        # Associate product 3
        wizard_form = Form(
            self.wizard_model.with_context(
                active_model="product.product", active_id=product_3.id
            )
        )
        wizard_form.destination_template_id = tmpl
        wizard_form.selected_value_ids.add(self.value3)
        wizard = wizard_form.save()
        # Attribute 1 should be setup to continue
        with self.assertRaises(UserError):
            wizard.action_change_template()

        wizard_form = Form(
            wizard.with_context(active_model="product.product", active_id=product_3.id)
        )
        wizard_form.selected_value_ids.add(self.value2)
        wizard = wizard_form.save()
        wizard.action_change_template()

        self.assertEqual(product_3.product_tmpl_id, tmpl)
        self.assertEqual(product_1.lst_price, 100.0)
        self.assertEqual(product_2.lst_price, 150.0)
        self.assertEqual(product_3.lst_price, 130.0)
        self.assertFalse(product_tmpl_3.active)

        # Associate product 4
        wizard_form = Form(
            self.wizard_model.with_context(
                active_model="product.product", active_id=product_4.id
            )
        )
        wizard_form.destination_template_id = tmpl
        wizard_form.selected_value_ids.add(self.value2)
        wizard_form.selected_value_ids.add(self.value4)
        wizard = wizard_form.save()
        wizard.action_change_template()

        self.assertEqual(product_4.product_tmpl_id, tmpl)
        self.assertEqual(product_1.lst_price, 100.0)
        self.assertEqual(product_2.lst_price, 150.0)
        self.assertEqual(product_3.lst_price, 130.0)
        self.assertEqual(product_4.lst_price, 180.0)
        self.assertFalse(product_tmpl_4.active)

        # Associate product 5 with different uom
        wizard_form = Form(
            self.wizard_model.with_context(
                active_model="product.product", active_id=product_5.id
            )
        )
        wizard_form.destination_template_id = tmpl
        wizard = wizard_form.save()
        self.assertTrue(wizard.is_different_uom)
