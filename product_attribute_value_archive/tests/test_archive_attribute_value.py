# Copyright 2021 Camptocamp SA
# Copyright 2026 Mario Castillo López <@mcastillol14>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestArchiveAttributeValue(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpClassTemplate()
        cls.setUpClassAttribute()
        cls.setUpClassProduct()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.setUpClassCommon()

    @classmethod
    def setUpClassTemplate(cls):
        cls.template_model = cls.env["product.template"]
        cls.pen = cls.template_model.create({"name": "pen"})
        cls.car = cls.template_model.create({"name": "car"})

    @classmethod
    def setUpClassAttribute(cls):
        cls.attribute_model = cls.env["product.attribute"]
        cls.value_model = cls.env["product.attribute.value"]
        cls.attribute_line_model = cls.env["product.template.attribute.line"]
        cls.attribute_value_model = cls.env["product.template.attribute.value"]
        cls.attribute = cls.attribute_model.create({"name": "color"})
        cls.values = cls.env["product.attribute.value"]
        for color in ["red", "blue", "green", "black"]:
            value = cls.value_model.create(
                {"attribute_id": cls.attribute.id, "name": color}
            )
            setattr(cls, color, value)
            cls.values |= value

    @classmethod
    def setUpClassProduct(cls):
        cls.product_model = cls.env["product.product"]
        cls.pen_attribute_line = cls.attribute_line_model.create(
            {
                "product_tmpl_id": cls.pen.id,
                "attribute_id": cls.attribute.id,
                "value_ids": [(6, 0, cls.values.ids)],
            }
        )
        cls.car_attribute_line = cls.attribute_line_model.create(
            {
                "product_tmpl_id": cls.car.id,
                "attribute_id": cls.attribute.id,
                "value_ids": [(6, 0, cls.values.ids)],
            }
        )
        cls.attribute_lines = cls.pen_attribute_line | cls.car_attribute_line

    @classmethod
    def setUpClassCommon(cls):
        cls.red_template_values = cls.attribute_value_model.search(
            [("product_attribute_value_id", "=", cls.red.id)]
        )
        cls.red_products = cls.red_template_values.ptav_product_variant_ids
        cls.red_templates = cls.red_products.mapped("product_tmpl_id")
        # Probably a way to do better
        pen_template_value = cls.attribute_value_model.search(
            [
                ("product_attribute_value_id", "=", cls.red.id),
                ("attribute_line_id", "=", cls.pen_attribute_line.id),
            ]
        )
        cls.red_pen = pen_template_value.ptav_product_variant_ids
        # sale.sale_order_1 is demo data, not loaded by default since 19.0
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    @classmethod
    def _create_sale_order_lines(cls, products):
        vals = []
        for product in products:
            vals.append(
                {
                    "product_id": product.id,
                    "product_uom_qty": 1,
                    "order_id": cls.order.id,
                }
            )
        cls.env["sale.order.line"].create(vals)
        return cls.order

    @classmethod
    def _get_template_line_from_templates(cls, product_tmpls):
        return cls.attribute_line_model.search(
            [
                "|",
                ("active", "=", True),
                ("active", "=", False),
                ("product_tmpl_id", "in", product_tmpls.ids),
            ]
        )

    def assertNone(self, iterable):
        return self.assertFalse(any(iterable))

    def assertAll(self, iterable):
        return self.assertTrue(all(iterable))

    def test_value_unlink(self):
        # No SO has been created, therefore we should be able to unlink values.
        other_color_values = self.values - self.red
        # Remove red from the attribute lines
        self.attribute_lines.write({"value_ids": [(6, 0, other_color_values.ids)]})
        self.red.unlink()
        updated_values = self.attribute.value_ids
        self.assertEqual(len(updated_values), 3)
        self.assertNotIn(self.red, updated_values)

    def test_value_archive(self):
        self._create_sale_order_lines(self.red_products)
        # unlink should fail here, red is still used by car and pen
        regex = f"You cannot delete the value color: {self.red.name}"
        with self.assertRaisesRegex(UserError, regex):
            self.red.unlink()
        # Remove the value from the set
        self.attribute_lines.write({"value_ids": [(3, self.red.id, 0)]})
        # odoo archives the variant instead of deleting it, it's on a sale.order.line
        self.assertNone(self.red_products.mapped("active"))
        # now that the variant is archived, unlink should go through
        self.red.unlink()
        self.assertFalse(self.red.active)

    def test_value_non_archiveable(self):
        self._create_sale_order_lines(self.red_pen)
        # Remove the value from the set
        self.pen_attribute_line.value_ids = [(3, self.red.id, 0)]
        # archived instead of unlinked, it's referenced by a sale.order.line
        self.assertFalse(self.red_pen.active)
        # red is still used by car, so unlink should raise
        regex = (
            f"You cannot delete the value color: {self.red.name} "
            f"because it is used on the following products:\n{self.car.name}"
        )
        with self.assertRaisesRegex(UserError, regex):
            self.red.unlink()

    # matching an archived value should unarchive it, not duplicate it
    def test_create_same_value_after_archive(self):
        self._create_sale_order_lines(self.red_products)
        # Remove the red value from the set
        self.attribute_lines.write({"value_ids": [(3, self.red.id, 0)]})
        # now that the variant is archived, unlink should go through
        self.red.unlink()
        self.assertFalse(self.red.active)
        new_red = self.value_model.create(
            {"attribute_id": self.attribute.id, "name": "red"}
        )
        self.assertEqual(new_red, self.red)
        self.assertTrue(new_red.active)

    # unarchiving a variant should cascade back to its attribute value
    def test_unarchive_variant_after_value_archive(self):
        self._create_sale_order_lines(self.red_products)
        # Remove the red value from the set
        self.attribute_lines.write({"value_ids": [(3, self.red.id, 0)]})
        # now that the variant is archived, unlink should go through
        self.red.unlink()
        self.assertFalse(self.red.active)
        # Ensure that odoo sets all ptav to active False when once unreferenced
        product_tmpl_attribute_vals = (
            self.red_products.product_template_attribute_value_ids
        )
        self.assertNone(product_tmpl_attribute_vals.mapped("ptav_active"))
        # unarchiving the products should also unarchive the attribute value
        self.red_products.write({"active": True})
        self.assertTrue(self.red.active)
        self.assertAll(product_tmpl_attribute_vals.mapped("ptav_active"))

    # unarchiving a variant should cascade up through ptav, pav and the tmpl_attr_line
    def test_unarchive_product_archived_tmpl_attr_line(self):
        self._create_sale_order_lines(self.red_products)
        # removing the line archives it, and the variant along with it
        self.red_templates.write({"attribute_line_ids": [(5, 0, 0)]})
        template_lines = self._get_template_line_from_templates(self.red_templates)
        self.assertEqual(len(template_lines), 2)
        self.assertNone(template_lines.mapped("active"))
        # the related variants are already archived, so this just archives the value
        self.red.unlink()
        self.assertNone(self.red_products.mapped("active"))
        self.red_products.write({"active": True})
        tmpl_attr_vals = self.red_products.mapped(
            "product_template_attribute_value_ids"
        )
        self.assertAll(tmpl_attr_vals.mapped("ptav_active"))
        attr_vals = tmpl_attr_vals.mapped("product_attribute_value_id")
        self.assertAll(attr_vals.mapped("active"))
        template_lines = self.red_templates.mapped("attribute_line_ids")
        self.assertAll(template_lines.mapped("active"))
        self.assertEqual(len(template_lines), 2)
