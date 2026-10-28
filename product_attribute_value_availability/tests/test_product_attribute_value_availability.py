# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.product.tests.common import ProductAttributesCommon


class TestProductAttributeValueAvailability(ProductAttributesCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env["product.template"].create(
            {
                "name": "Steak",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.color_attribute.id,
                            "value_ids": [
                                Command.set(
                                    (
                                        cls.color_attribute_red
                                        | cls.color_attribute_blue
                                    ).ids
                                )
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.no_variant_attribute.id,
                            "value_ids": [
                                Command.set(cls.no_variant_attribute.value_ids.ids)
                            ],
                        }
                    ),
                ],
            }
        )
        ptavs = cls.template.attribute_line_ids.product_template_value_ids

        def get_ptav(pav):
            return ptavs.filtered(lambda ptav: ptav.product_attribute_value_id == pav)

        cls.ptav_red = get_ptav(cls.color_attribute_red)
        cls.ptav_blue = get_ptav(cls.color_attribute_blue)
        cls.ptav_extra = get_ptav(cls.no_variant_attribute_extra)
        cls.ptav_second = get_ptav(cls.no_variant_attribute_second)

    def test_variant_value_unavailable(self):
        combination = self.ptav_red | self.ptav_second
        self.assertTrue(self.template._is_combination_possible(combination))
        self.color_attribute_red.is_available = False
        self.assertFalse(self.template._is_combination_possible(combination))
        self.assertIn(
            self.ptav_red.id,
            self.template._get_attribute_exclusions()["unavailable_ptav_ids"],
        )
        self.color_attribute_red.is_available = True
        self.assertTrue(self.template._is_combination_possible(combination))

    def test_no_variant_value_unavailable(self):
        combination = self.ptav_blue | self.ptav_extra
        self.assertTrue(self.template._is_combination_possible(combination))
        self.no_variant_attribute_extra.is_available = False
        self.assertFalse(self.template._is_combination_possible(combination))
        self.assertTrue(
            self.template._is_combination_possible(
                self.ptav_blue, ignore_no_variant=True
            )
        )

    def test_structure_unchanged(self):
        variants = self.template.product_variant_ids
        self.color_attribute_red.is_available = False
        self.no_variant_attribute_extra.is_available = False
        self.template._create_variant_ids()
        self.assertEqual(self.template.product_variant_ids, variants)
        self.assertTrue(all((self.ptav_red | self.ptav_extra).mapped("ptav_active")))
