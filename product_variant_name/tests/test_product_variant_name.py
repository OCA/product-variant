# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase


class TestProductVariantName(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_tmpl_model = self.env["product.template"]
        self.product_model = self.env["product.product"]

    def test_product_variant_name(self):
        # Create a product template and check that variant is created with the
        # same name
        product_tmpl = self.product_tmpl_model.create({"name": "Test Template"})
        self.assertEqual(product_tmpl.product_variant_id.name, product_tmpl.name)
        # Modify variant name and check the difference
        product_tmpl.product_variant_id.write({"name": "Test Variant"})
        self.assertNotEqual(product_tmpl.product_variant_id.name, product_tmpl.name)

    def test_create_variant_without_template(self):
        # Create variants without template and check that their template is
        # created with the variant name and the template values
        products = self.product_model.create(
            [
                {"name": "Test Variant 1", "type": "service"},
                {"name": "Test Variant 2", "list_price": 12.0},
            ]
        )
        self.assertEqual(
            products.product_tmpl_id.mapped("name"), products.mapped("name")
        )
        self.assertEqual(products[0].product_tmpl_id.type, "service")
        self.assertEqual(products[1].product_tmpl_id.list_price, 12.0)
        for product in products:
            self.assertEqual(product.product_tmpl_id.product_variant_ids, product)
