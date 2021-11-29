# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError
from odoo.tests.common import Form, SavepointCase
from odoo.tools import mute_logger


class TestArchiveAttributeValue(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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

    @classmethod
    def _create_sale_order(cls, products):
        """Create a sale order with given products."""
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.partner
        with mute_logger("odoo.tests.common.onchange"):
            for product in products:
                with sale_form.order_line.new() as line:
                    line.product_id = product
                    line.product_uom_qty = 1
        return sale_form.save()

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
        # then unlink it
        self.red.unlink()
        updated_values = self.attribute.value_ids
        self.assertEqual(len(updated_values), 3)
        self.assertNotIn(self.red, updated_values)

    def test_value_archive(self):
        self._create_sale_order(self.red_products)
        # Trying to unlink the value here should raise an exception
        # since it's still referenced by the car and pen product templates
        regex = f"You cannot delete the value color: {self.red.name}"
        with self.assertRaisesRegex(UserError, regex):
            self.red.unlink()
        # Remove the value from the set
        self.attribute_lines.write({"value_ids": [(3, self.red.id, 0)]})
        # The variants should be archived instead of unlinked,
        # since it's referenced by a sale.order.line (odoo standard)
        self.assertNone(self.red_products.mapped("active"))
        # now, since the the variant is archived, we shouldn't be able
        self.red.unlink()
        self.assertFalse(self.red.active)

    def test_value_non_archiveable(self):
        self._create_sale_order(self.red_pen)
        # Remove the value from the set
        self.pen_attribute_line.value_ids = [(3, self.red.id, 0)]
        # The variant should be archived, since it's referenced
        # by a sale.order.line -> odoo standard
        self.assertFalse(self.red_pen.active)
        # The red car variant is still active, so we shouldn't be able
        # to archive or unlink the value, and odoo should raise
        # an exception saying that red is still referenced by car
        regex = r"You cannot delete the value color: {value}.*{product}".format(
            value=self.red.name, product=self.car.name
        )
        with self.assertRaisesRegex(UserError, regex):
            self.red.unlink()

    def test_create_same_value_after_archive(self):
        """If we try to create the same attribute value as an existing archived
        one, then it should be unarchived instead.
        """
        self._create_sale_order(self.red_products)
        # Remove the red value from the set
        self.attribute_lines.write({"value_ids": [(3, self.red.id, 0)]})
        # now, since the the variant is archived, we shouldn't be able
        self.red.unlink()
        self.assertFalse(self.red.active)
        new_red = self.value_model.create(
            {"attribute_id": self.attribute.id, "name": "red"}
        )
        self.assertEqual(new_red, self.red)
        self.assertTrue(new_red.active)

    def test_unarchive_variant_after_value_archive(self):
        """An archived attribute value should be unarchived if a variant
        that references it is unarchived.
        """
        self._create_sale_order(self.red_products)
        # Remove the red value from the set
        self.attribute_lines.write({"value_ids": [(3, self.red.id, 0)]})
        # now, since the the variant is archived, we shouldn't be able
        self.red.unlink()
        self.assertFalse(self.red.active)
        # Ensure that odoo sets all ptav to active False when once unreferenced
        product_tmpl_attribute_vals = (
            self.red_products.product_template_attribute_value_ids
        )
        self.assertNone(product_tmpl_attribute_vals.mapped("ptav_active"))
        # Unarchive products, and check that attribute value is unarchived as
        # well
        self.red_products.write({"active": True})
        self.assertTrue(self.red.active)
        self.assertAll(product_tmpl_attribute_vals.mapped("ptav_active"))

    def test_unarchive_product_archived_tmpl_attr_line(self):
        """docstring here
        """
        self._create_sale_order(self.red_products)
        # Removing the tmpl_attr_line from the product templates
        # should archive it, as well as the variant
        self.red_templates.write({"attribute_line_ids": [(5, 0, 0)]})
        template_lines = self._get_template_line_from_templates(self.red_templates)
        self.assertEqual(len(template_lines), 2)
        self.assertNone(template_lines.mapped("active"))
        # Since the the related variants are archived, removing a value from
        # an attribute should archive it instead or unlink
        self.red.unlink()
        self.assertNone(self.red_products.mapped("active"))
        # Unarchive those variants should as well unarchive :
        #   - the related product_template_attribute_value
        #   - the related product_attribute_value
        #   - the related product_template_attribute_line
        self.red_products.write({"active": True})
        # Check product_template_attribute_value
        tmpl_attr_vals = self.red_products.mapped(
            "product_template_attribute_value_ids"
        )
        self.assertAll(tmpl_attr_vals.mapped("ptav_active"))
        # Check product_attribute_value
        attr_vals = tmpl_attr_vals.mapped("product_attribute_value_id")
        self.assertAll(attr_vals.mapped("active"))
        # Check product_template_attribute_line
        template_lines = self.red_templates.mapped("attribute_line_ids")
        self.assertAll(template_lines.mapped("active"))
        self.assertEqual(len(template_lines), 2)
