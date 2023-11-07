# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestProductVariantTreeQtyAvailable(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product_product = cls.env["product.product"]
        cls.stock_quant = cls.env["stock.quant"]
        cls.product_1 = cls.product_product.create({"name": "Product 1"})

    def test_action_open_product_quants(self):
        result = self.product_1.action_open_product_quants()
        action_name = ("%s - Update Quantity") % self.product_1.display_name
        self.assertEqual(
            result["name"],
            action_name,
            msg="Action name must be equal '%s'" % action_name,
        )

    def test_search_on_hand(self):
        with self.assertRaises(UserError, msg="Operation not supported"):
            self.stock_quant._search_on_hand("", False)

        # operator: "!=", value: True
        result = self.stock_quant._search_on_hand("!=", True)
        self.assertEqual(result[0][1], "not in", msg="Operator must be equal 'not in'")

        # operator: "=", value: False
        result = self.stock_quant._search_on_hand("=", False)
        self.assertEqual(result[0][1], "not in", msg="Operator must be equal 'not in'")

        # operator: "!=", value: False
        result = self.stock_quant._search_on_hand("!=", False)
        self.assertEqual(result[0][1], "in", msg="Operator must be equal 'in'")

        # operator: "=", value: True
        result = self.stock_quant._search_on_hand("=", True)
        self.assertEqual(result[0][1], "in", msg="Operator must be equal 'in'")
