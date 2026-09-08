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
