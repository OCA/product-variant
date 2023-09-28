# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import TransactionCase


class TestProductVariantDescription(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_tmpl_model = self.env["product.template"]
        self.product_model = self.env["product.product"]

        self.uom_unit = self.env.ref("uom.product_uom_unit")

        self.color_attribute = self.env["product.attribute"].create(
            {
                "name": "Base Color",
                "value_ids": [
                    Command.create({"name": "red", "sequence": 1}),
                    Command.create({"name": "white", "sequence": 2}),
                ],
            }
        )

    def test_01_product_variant_description_single_variant(self):
        # Create a product template and check that variant is created with the
        # same description
        product_tmpl = self.product_tmpl_model.create(
            {
                "name": "Test Template",
                "description": "Template description",
            }
        )
        self.assertEqual(
            product_tmpl.product_variant_id.description, product_tmpl.description
        )
        # With only one variant template and variant description must be kept aligned.
        product_tmpl.product_variant_id.write(
            {"description": "Change description in variant"}
        )
        self.assertEqual(
            product_tmpl.product_variant_id.description, product_tmpl.description
        )

    def test_02_product_variant_description_multiple_variants(self):
        template = self.env["product.template"].create(
            {
                "name": "Sofa",
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "description": "Template description",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.color_attribute.id,
                            "value_ids": [
                                Command.link(self.color_attribute.value_ids[0].id),
                                Command.link(self.color_attribute.value_ids[1].id),
                            ],
                        }
                    ),
                ],
            }
        )
        self.assertEqual(len(template.product_variant_ids), 2)
        variant_1 = template.product_variant_ids[0]
        variant_2 = template.product_variant_ids[1]
        self.assertEqual(template.description, variant_1.description)
        self.assertEqual(template.description, variant_2.description)
        variant_1.write({"description": "Description for variant 1"})
        self.assertNotEqual(template.description, variant_1.description)
        variant_2.write({"description": "Another description for variant 2"})
        self.assertNotEqual(template.description, variant_2.description)
        self.assertNotEqual(variant_1.description, variant_2.description)
        # As soon as any variant description changed, description should have
        # been cleared in the template.
        self.assertFalse(template.description)
