# Copyright 2020 Studio73 - Miguel Gandia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestProductTemplateAttributeValue(common.TransactionCase):
    def setUp(self):
        super(TestProductTemplateAttributeValue, self).setUp()

        product_attributes = self.env["product.attribute"].create(
            [
                {"name": "PA1", "create_variant": "always", "sequence": 1},
                {"name": "PA2", "create_variant": "always", "sequence": 2},
                {"name": "PA3", "create_variant": "dynamic", "sequence": 3},
                {"name": "PA4", "create_variant": "no_variant", "sequence": 4},
            ]
        )

        self.env["product.attribute.value"].create(
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

        self.matrix_template2 = self.env["product.template"].create(
            {
                "name": "Matrix",
                "type": "consu",
                "uom_id": self.ref("uom.product_uom_unit"),
                "uom_po_id": self.ref("uom.product_uom_unit"),
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
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
