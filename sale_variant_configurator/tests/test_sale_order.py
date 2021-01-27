# Copyright 2017 David Vidal
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestSaleOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Environments
        cls.product_attribute = cls.env["product.attribute"]
        cls.product_attribute_value = cls.env["product.attribute.value"]
        cls.product_template = cls.env["product.template"].with_context(
            check_variant_creation=True
        )
        cls.sale_order = cls.env["sale.order"]
        cls.product_product = cls.env["product.product"]
        cls.sale_order_line = cls.env["sale.order.line"]
        cls.res_partner = cls.env["res.partner"]
        cls.product_category = cls.env["product.category"]
        # Instances
        cls.category1 = cls.product_category.create(
            {"name": "No create variants category"}
        )
        cls.attribute1 = cls.product_attribute.create(
            {"name": "Color (sale_variante_configurator)"}
        )
        cls.value1 = cls.product_attribute_value.create(
            {"name": "Red", "attribute_id": cls.attribute1.id}
        )
        cls.value2 = cls.product_attribute_value.create(
            {"name": "Green", "attribute_id": cls.attribute1.id}
        )
        cls.product_template_yes = cls.product_template.create(
            {
                "name": "Product template 1",
                "list_price": 100,
                "no_create_variants": "yes",
                "categ_id": cls.category1.id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute1.id,
                            "value_ids": [(6, 0, [cls.value1.id, cls.value2.id])],
                        },
                    )
                ],
            }
        )
        cls.product_template_no = cls.product_template.create(
            {
                "name": "Product template 2",
                "list_price": 100,
                "categ_id": cls.category1.id,
                "no_create_variants": "no",
                "description_sale": "Template description",
            }
        )
        cls.attr_lines = cls.product_template_yes.attribute_line_ids
        cls.ptav_1 = cls.attr_lines.product_template_value_ids.filtered(
            lambda x: x.product_attribute_value_id == cls.value1[0]
        )
        cls.ptav_1.price_extra = 10
        cls.customer = cls.res_partner.create({"name": "Customer 1"})

    def test_onchange_product_tmpl_id(self):
        sale = self.sale_order.create({"partner_id": self.customer.id})
        line1 = self.sale_order_line.new(
            {
                "order_id": sale.id,
                "product_tmpl_id": self.product_template_yes.id,
                "price_unit": 100,
                "product_uom": self.product_template_yes.uom_id.id,
                "product_uom_qty": 1,
            }
        )
        result = line1._onchange_product_tmpl_id_configurator()
        self.assertEqual(len(line1.product_attribute_ids), 1)
        expected_domain = [("product_tmpl_id", "=", self.product_template_yes.id)]
        self.assertEqual(result["domain"]["product_id"], expected_domain)
        line2 = self.sale_order_line.new(
            {
                "order_id": sale.id,
                "product_tmpl_id": self.product_template_no.id,
                "product_uom": self.product_template_no.uom_id.id,
                "product_uom_qty": 1,
                "price_unit": 200,
                "name": "Line 2",
            }
        )
        line2._onchange_product_tmpl_id_configurator()
        line2._onchange_product_id_configurator()
        line2.product_id_change()
        self.assertEqual(line2.product_id, self.product_template_no.product_variant_ids)
        self.assertEqual(
            line2.name,
            "%s\n%s"
            % (
                self.product_template_no.name,
                (self.product_template_no.description_sale),
            ),
        )

    def test_onchange_product_attribute_ids(self):
        sale = self.sale_order.create({"partner_id": self.customer.id})
        line = self.sale_order_line.new(
            {
                "order_id": sale.id,
                "product_tmpl_id": self.product_template_yes.id,
                "price_unit": 0,
                "name": "Line 1",
                "product_uom_qty": 1,
                "product_uom": self.product_template_yes.uom_id.id,
            }
        )
        line._onchange_product_tmpl_id_configurator()
        self.assertEqual(line.price_unit, 100)  # List price
        line.product_attribute_ids[0].value_id = self.value1.id
        result = line._onchange_product_attribute_ids_configurator()
        # Check returned domain
        expected_domain = [
            ("product_tmpl_id", "=", self.product_template_yes.id),
            ("product_template_attribute_value_ids", "=", self.ptav_1.id),
        ]
        self.assertDictEqual(result["domain"], {"product_id": expected_domain})
        # Check price brought to line with extra
        self.assertEqual(line.price_unit, 110)

    def test_onchange_product_attribute_ids2(self):
        sale = self.sale_order.create({"partner_id": self.customer.id})
        # Create product and onchange again to see if the product is selected
        product = self.product_product.create(
            {
                "product_tmpl_id": self.product_template_yes.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_template_yes.id,
                            "attribute_id": self.attribute1.id,
                            "value_id": self.value1.id,
                            "owner_model": "sale.order.line",
                        },
                    )
                ],
            }
        )
        line = self.sale_order_line.new(
            {
                "order_id": sale.id,
                "product_tmpl_id": self.product_template_yes.id,
                "price_unit": 0,
                "name": "Line 1",
                "product_uom_qty": 1,
                "product_uom": self.product_template_yes.uom_id.id,
            }
        )
        line._onchange_product_tmpl_id_configurator()
        line.product_attribute_ids[0].value_id = self.value1.id
        line._onchange_product_attribute_ids_configurator()
        self.assertEqual(line.product_id, product)

    def test_can_create_product_variant(self):
        sale = self.sale_order.create({"partner_id": self.customer.id})
        line = self.sale_order_line.new(
            {
                "order_id": sale.id,
                "product_tmpl_id": self.product_template_yes.id,
                "price_unit": 100,
                "name": "Line 1",
                "product_uom": self.product_template_yes.uom_id.id,
            }
        )
        self.assertFalse(line.can_create_product)
        attributes = self.env["product.configurator.attribute"].create(
            {
                "product_tmpl_id": self.product_template_yes.id,
                "attribute_id": self.attribute1.id,
                "value_id": self.value1.id,
                "owner_model": "sale.order.line",
                "owner_id": line.id,
            }
        )
        line.product_attribute_ids = attributes
        line._onchange_product_attribute_ids_configurator()
        self.assertTrue(line.can_create_product)
        line.create_product_variant = True
        line._onchange_create_product_variant()
        self.assertTrue(line.product_id)
        self.assertFalse(line.create_product_variant)

    def test_onchange_product_id(self):
        product = self.product_product.create(
            {
                "product_tmpl_id": self.product_template_yes.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_template_yes.id,
                            "attribute_id": self.attribute1.id,
                            "value_id": self.value1.id,
                        },
                    )
                ],
            }
        )
        order = self.sale_order.create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "price_unit": 100,
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "product_uom": product.uom_id.id,
                        },
                    )
                ],
            }
        )
        line = order.order_line[0]
        with self.cr.savepoint():
            line.product_id_change()
            line._onchange_product_id_configurator()
            self.assertEqual(len(line.product_attribute_ids), 1)
            self.assertEqual(line.product_tmpl_id, self.product_template_yes)

    def test_action_confirm(self):
        order = self.sale_order.create({"partner_id": self.customer.id})
        line_1 = self.sale_order_line.new(
            {
                "order_id": order.id,
                "product_tmpl_id": self.product_template_yes.id,
                "price_unit": 100,
                "name": "Line 1",
                "product_uom_qty": 1,
                "product_uom": self.product_template_yes.uom_id.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_template_yes.id,
                            "attribute_id": self.attribute1.id,
                            "value_id": self.value1.id,
                            "owner_model": "sale.order.line",
                        },
                    )
                ],
                "create_product_variant": True,
            }
        )
        line_2 = self.sale_order_line.new(
            {
                "order_id": order.id,
                "product_tmpl_id": self.product_template_no.id,
                "product_uom": self.product_template_no.uom_id.id,
                "product_uom_qty": 1,
                "price_unit": 200,
                "name": "Line 2",
                "create_product_variant": True,
            }
        )
        for line in (line_1, line_2):
            line._onchange_product_tmpl_id_configurator()
            line._onchange_product_id_configurator()
            line.product_id_change()
            line._onchange_product_attribute_ids_configurator()
            if line.can_create_product:
                line.create_variant_if_needed()
                line.create_product_variant = True
                line._onchange_create_product_variant()
        order.write({"order_line": [(4, line_1.id), (4, line_2.id)]})
        order.action_confirm()
        order_line_without_product = order.order_line.filtered(
            lambda x: not x.product_id
        )
        self.assertEqual(
            len(order_line_without_product), 0, "All purchase lines must have a product"
        )
