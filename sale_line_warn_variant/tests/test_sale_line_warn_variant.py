##############################################################################
# Copyright (c) 2025 braintec AG (https://braintec.com)
# All Rights Reserved
#
# Licensed under the AGPL-3.0 (http://www.gnu.org/licenses/agpl.html)
# See LICENSE file for full licensing details.
##############################################################################

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleLineWarnVariant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Configure test data."""
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.product_with_warning = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "variant_sale_line_warn": "warning",
                "variant_sale_line_warn_msg": "Highly corrosive",
            }
        )
        cls.product_with_block = cls.env["product.product"].create(
            {
                "name": "Test Product (2)",
                "variant_sale_line_warn": "block",
                "variant_sale_line_warn_msg": "Not produced anymore",
            }
        )

    def test_variant_sale_warnings(self):
        """Warnings & SO/SOL updates products with variant sale warnings are used."""
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})

        sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_with_warning.id,
            }
        )
        warning = sale_order_line._onchange_product_id_warning()
        self.assertDictEqual(
            warning,
            {
                "warning": {
                    "title": "Warning for Test Product",
                    "message": self.product_with_warning.variant_sale_line_warn_msg,
                },
            },
        )

        sale_order_line.product_id = self.product_with_block
        warning = sale_order_line._onchange_product_id_warning()

        self.assertDictEqual(
            warning,
            {
                "warning": {
                    "title": "Warning for Test Product (2)",
                    "message": self.product_with_block.variant_sale_line_warn_msg,
                },
            },
        )

        self.assertFalse(sale_order_line.product_id.id)

        warning = (
            sale_order_line._onchange_product_id_warning()
        )  # no product_id. For coverage
        self.assertFalse(warning)

        # Taken from product template (not variant) if any
        self.product_with_warning.write(
            {
                "sale_line_warn": "warning",
                "sale_line_warn_msg": "Highly corrosive Template",
            }
        )
        sale_order_line.product_id = self.product_with_warning
        warning = sale_order_line._onchange_product_id_warning()
        self.assertDictEqual(
            warning,
            {
                "warning": {
                    "title": "Warning for Test Product",
                    "message": self.product_with_warning.sale_line_warn_msg,
                },
            },
        )

    def test_catalog_info(self):
        """Catalog displays proper warning information."""
        sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        products = self.product_with_warning | self.product_with_block

        products_catalog = sale_order._get_product_catalog_order_line_info(products.ids)

        self.assertEqual(
            products_catalog[self.product_with_warning.id]["warning"],
            self.product_with_warning.variant_sale_line_warn_msg,
        )
        self.assertFalse(products_catalog[self.product_with_warning.id]["readOnly"])
        self.assertEqual(
            products_catalog[self.product_with_block.id]["warning"],
            self.product_with_block.variant_sale_line_warn_msg,
        )
        self.assertTrue(products_catalog[self.product_with_block.id]["readOnly"])

        self.env["sale.order.line"].create(
            [
                {
                    "order_id": sale_order.id,
                    "product_id": self.product_with_warning.id,
                },
                {
                    "order_id": sale_order.id,
                    "product_id": self.product_with_warning.id,
                },
                {
                    "order_id": sale_order.id,
                    "product_id": self.product_with_block.id,
                },
            ]
        )
        products_catalog = sale_order._get_product_catalog_order_line_info(products.ids)
        self.assertEqual(
            products_catalog[self.product_with_warning.id]["warning"],
            self.product_with_warning.variant_sale_line_warn_msg,
        )
        self.assertTrue(products_catalog[self.product_with_warning.id]["readOnly"])
        self.assertEqual(
            products_catalog[self.product_with_block.id]["warning"],
            self.product_with_block.variant_sale_line_warn_msg,
        )
        self.assertTrue(products_catalog[self.product_with_block.id]["readOnly"])
