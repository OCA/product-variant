# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestProductPrice(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.pricelist_base = cls.env["product.pricelist"].create(
            {
                "name": "Base Pricelist",
            }
        )
        cls.color = cls.env["product.attribute"].create(
            {
                "name": "Color Variant",
            }
        )
        cls.size = cls.env["product.attribute"].create(
            {
                "name": "Size Variant",
            }
        )

        cls.attribute_color_red = cls.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": cls.color.id,
            }
        )

        cls.attribute_color_blue = cls.env["product.attribute.value"].create(
            {
                "name": "Blue",
                "attribute_id": cls.color.id,
            }
        )

        cls.attribute_size_m = cls.env["product.attribute.value"].create(
            {
                "name": "M",
                "attribute_id": cls.size.id,
            }
        )

        cls.attribute_size_s = cls.env["product.attribute.value"].create(
            {
                "name": "S",
                "attribute_id": cls.size.id,
            }
        )

        cls.template = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "list_price": 10.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.color.id,
                            "value_ids": [
                                Command.link(cls.attribute_color_blue.id),
                                Command.link(cls.attribute_color_red.id),
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.size.id,
                            "value_ids": [
                                Command.link(cls.attribute_size_m.id),
                                Command.link(cls.attribute_size_s.id),
                            ],
                        }
                    ),
                ],
            }
        )
        cls.product_red_s = cls.template.product_variant_ids.filtered(
            lambda p: cls.attribute_color_red.id
            in p.product_template_attribute_value_ids.product_attribute_value_id.ids
            and cls.attribute_size_s.id
            in p.product_template_attribute_value_ids.product_attribute_value_id.ids
        )
        cls.pricelist_base.write(
            {
                "item_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_red_s.id,
                            "applied_on": "0_product_variant",
                            "fixed_price": 6.0,
                        }
                    )
                ]
            }
        )

        cls.product_red_m = cls.template.product_variant_ids.filtered(
            lambda p: cls.attribute_color_red.id
            in p.product_template_attribute_value_ids.product_attribute_value_id.ids
            and cls.attribute_size_m.id
            in p.product_template_attribute_value_ids.product_attribute_value_id.ids
        )
        cls.pricelist_base.write(
            {
                "item_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_red_m.id,
                            "applied_on": "0_product_variant",
                            "fixed_price": 5.0,
                        }
                    )
                ]
            }
        )

        cls.env.company.price_display_variant_pricelist_id = cls.pricelist_base

    def test_price(self):
        self.assertEqual(6.0, self.product_red_s.pricelist_base_price)
        self.assertEqual(5.0, self.product_red_m.pricelist_base_price)
        self.assertEqual(self.pricelist_base, self.product_red_m.base_pricelist_id)
