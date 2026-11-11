# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon

TEST_IMAGE = (
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8"
    b"/wcAAgAB/UTeG8kAAAAASUVORK5CYII="
)


class ProductVariantReassignCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.att_color = cls.env["product.attribute"].create({"name": "Color (test)"})
        cls.att_size = cls.env["product.attribute"].create({"name": "Size (test)"})
        cls.att_origin = cls.env["product.attribute"].create(
            {"name": "Origin (test)", "create_variant": "no_variant"}
        )
        cls.att_color_blue = cls.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": cls.att_color.id}
        )
        cls.att_color_red = cls.env["product.attribute.value"].create(
            {"name": "Red", "attribute_id": cls.att_color.id}
        )
        cls.att_color_green = cls.env["product.attribute.value"].create(
            {"name": "Green", "attribute_id": cls.att_color.id}
        )
        cls.att_sice_xxl = cls.env["product.attribute.value"].create(
            {"name": "XXL", "attribute_id": cls.att_size.id}
        )
        cls.att_origin_nepal = cls.env["product.attribute.value"].create(
            {"name": "Nepal", "attribute_id": cls.att_origin.id}
        )
        cls.color_scarf = cls.env["product.template"].create(
            {
                "name": "Test color_scarf",
                "list_price": 25.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.att_color.id,
                            "value_ids": [
                                Command.set(
                                    [cls.att_color_blue.id, cls.att_color_red.id]
                                ),
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.att_origin.id,
                            "value_ids": [
                                Command.set([cls.att_origin_nepal.id]),
                            ],
                        }
                    ),
                ],
            }
        )
        cls.green_scarf = cls.env["product.template"].create(
            {
                "name": "Test color_scarf",
                "default_code": "TST-GREEN",
                "list_price": 30,
                "standard_price": 15,
                "barcode": "123456789012",
                "image_1920": TEST_IMAGE,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.att_size.id,
                            "value_ids": [
                                Command.set([cls.att_sice_xxl.id]),
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.att_origin.id,
                            "value_ids": [
                                Command.set([cls.att_origin_nepal.id]),
                            ],
                        }
                    ),
                ],
            }
        )

    @mute_logger("odoo.sql_db", "OpenUpgrade")
    def test_reassign_product(self):
        existing_color_scarves = self.color_scarf.product_variant_ids
        wiz_form = Form(
            self.env["reassign.variant"].with_context(active_id=self.green_scarf.id)
        )
        self.assertTrue(
            self.color_scarf in wiz_form.allowed_target_product_template_ids
        )
        wiz_form.target_product_template_id = self.color_scarf
        self.assertTrue(self.att_color_green in wiz_form.allowed_attribute_value_ids)
        self.assertFalse(self.att_color_red in wiz_form.allowed_attribute_value_ids)
        wiz_form.attribute_value_ids.add(self.att_color_green)
        wiz = wiz_form.save()
        wiz.reassign()
        new_color_scarve = self.color_scarf.product_variant_ids - existing_color_scarves
        self.assertEqual(
            new_color_scarve.product_template_attribute_value_ids.product_attribute_value_id,
            self.att_color_green,
        )
        self.assertEqual(new_color_scarve.default_code, "TST-GREEN")
        self.assertAlmostEqual(new_color_scarve.list_price, 30)
        self.assertAlmostEqual(new_color_scarve.standard_price, 15)
        self.assertEqual(new_color_scarve.barcode, "123456789012")
        self.assertEqual(new_color_scarve.image_variant_1920, TEST_IMAGE)
        self.assertFalse(bool(self.green_scarf.exists()))
        self.assertTrue(
            len(
                self.color_scarf.attribute_line_ids.filtered(
                    lambda x: x.attribute_id == self.att_origin
                )
            )
            == 1
        )
