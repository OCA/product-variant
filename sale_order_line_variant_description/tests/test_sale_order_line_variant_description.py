# Copyright 2015-17 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestSaleOrderLineVariantDescription(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.uom_uom_model = cls.env["uom.uom"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.so_model = cls.env["sale.order"]

    def test_product_id_change(self):
        uom = self.uom_uom_model.search([("name", "=", "Units")], limit=1)
        product_tmpl = self.product_tmpl_model.create(
            {
                "name": "Product template",
                "list_price": 121.0,
            }
        )
        product = product_tmpl.product_variant_id
        product.write(
            {
                "variant_description_sale": "Product variant description",
            }
        )
        so = self.so_model.create(
            {
                "partner_id": self.partner.id,
            }
        )
        so_line = self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "product_id": product.id,
                "product_uom_qty": 1.0,
                "product_uom": uom.id,
                "price_unit": 121.0,
            }
        )
        self.assertEqual(product.variant_description_sale, so_line.name)
