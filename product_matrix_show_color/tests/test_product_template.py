# Copyright 2020 Studio73 - Miguel Gandia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestProductTemplateAttributeValue(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        product_attributes = cls.env["product.attribute"].create(
            [
                {"name": "PA1_test", "create_variant": "always", "sequence": 1},
                {"name": "PA2_test", "create_variant": "always", "sequence": 2},
                {"name": "PA3_test", "create_variant": "dynamic", "sequence": 3},
                {"name": "PA4_test", "create_variant": "no_variant", "sequence": 4},
            ]
        )

        cls.env["product.attribute.value"].create(
            [
                {
                    "name": "PAV" + str(product_attribute.sequence) + str(i),
                    "html_color": "#24292e",
                    "attribute_id": product_attribute.id,
                }
                for i in range(1, 3)
                for product_attribute in product_attributes
            ]
        )

        cls.matrix_template2 = cls.env["product.template"].create(
            {
                "name": "Matrix",
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(attribute.value_ids.ids)],
                        },
                    )
                    for attribute in product_attributes
                ],
            }
        )

    def test_01_check__html_color_matrix(self):
        matrix = self.matrix_template2._get_template_matrix()
        self.assertEqual(
            matrix["header"][1]["html_color"], "#24292e", "Html color does not match"
        )
