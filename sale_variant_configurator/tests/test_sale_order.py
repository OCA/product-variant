# Copyright 2017 David Vidal
# Copyright 2024 Carolina Fernandez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import Form, common


class TestSaleOrder(common.TransactionCase):
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
                "description_sale": "Product template 1",
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
                "name": "Line 1",
                "product_tmpl_id": self.product_template_yes.id,
                "price_unit": 100,
                "product_uom": self.product_template_yes.uom_id.id,
                "product_uom_qty": 1,
            }
        )
        line1._onchange_product_tmpl_id_configurator()
        self.assertEqual(len(line1.product_attribute_ids), 1)
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        with order_form.order_line.new() as line_form:
            line_form.product_tmpl_id = self.product_template_no
        sale2 = order_form.save()
        line2 = sale2.order_line
        self.assertTrue(line2.product_id)
        self.assertEqual(line2.product_id, self.product_template_no.product_variant_ids)
        self.assertEqual(
            line2.name,
            "%s\n%s"
            % (
                self.product_template_no.name,
                (self.product_template_no.description_sale),
            ),
        )

    def test_sale_order_line_attribute_ids_01(self):
        product = self.product_product.create(
            {
                "name": self.product_template_yes.name,
                "list_price": 100,
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
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.customer
        with order_form.order_line.new() as line_form:
            line_form.product_tmpl_id = self.product_template_yes
            with line_form.product_attribute_ids.edit(0) as attribute_line_form:
                attribute_line_form.value_id = self.value1
        sale = order_form.save()
        line = sale.order_line
        self.assertEqual(line.price_unit, 110)
        self.assertEqual(line.price_extra, 10)
        self.assertEqual(line.price_unit + line.price_extra, 120)
        self.assertEqual(line.product_id, product)

    def _test_can_create_product_variant(self):
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
                "name": self.product_template_yes.name,
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
            line._onchange_product_id_configurator()
            self.assertEqual(len(line.product_attribute_ids), 2)
            self.assertEqual(line.product_tmpl_id, self.product_template_yes)

    def _test_action_confirm(self):
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
