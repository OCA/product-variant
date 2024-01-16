# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestSaleProductVariantAttributeTax(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax by attribute value", "amount": 10}
        )
        cls.tax2 = cls.env["account.tax"].create(
            {"name": "Replacement Tax", "amount": 10}
        )
        cls.fiscal_position = cls.env["account.fiscal.position"].create(
            {
                "name": "Test fiscal position",
                "tax_ids": [
                    (
                        0,
                        0,
                        {"tax_src_id": cls.tax.id, "tax_dest_id": cls.tax2.id},
                    ),
                ],
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Test", "property_account_position_id": False}
        )
        cls.attribute = cls.env["product.attribute"].create({"name": "Test attribute"})
        cls.attribute_value = cls.env["product.attribute.value"].create(
            {
                "name": "Test value",
                "attribute_id": cls.attribute.id,
                "tax_ids": [(6, 0, cls.tax.ids)],
            }
        )
        cls.attribute_value2 = cls.env["product.attribute.value"].create(
            {"name": "Test value 2", "attribute_id": cls.attribute.id}
        )
        obj = cls.env["product.template"].with_context(check_variant_creation=True)
        cls.product_template = obj.create(
            {
                "name": "Test template",
                "no_create_variants": "yes",
                "taxes_id": False,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, cls.attribute_value.ids)],
                        },
                    ),
                ],
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def test_select_attribute_wo_tax(self):
        line = self.env["sale.order.line"].new(
            {
                "order_id": self.order.id,
                "product_tmpl_id": self.product_template.id,
                "name": self.product_template.name,
                "product_uom_qty": 1,
                "product_uom": self.product_template.uom_id.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_template.id,
                            "attribute_id": self.attribute.id,
                            "value_id": self.attribute_value2.id,
                            "owner_model": "sale.order.line",
                        },
                    )
                ],
                "create_product_variant": True,
            }
        )
        line._onchange_product_attribute_ids_configurator()
        self.assertFalse(line.tax_id)

    def test_select_attribute_with_tax(self):
        line = self.env["sale.order.line"].new(
            {
                "order_id": self.order.id,
                "product_tmpl_id": self.product_template.id,
                "name": self.product_template.name,
                "product_uom_qty": 1,
                "product_uom": self.product_template.uom_id.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_template.id,
                            "attribute_id": self.attribute.id,
                            "value_id": self.attribute_value.id,
                            "owner_model": "sale.order.line",
                        },
                    )
                ],
                "create_product_variant": True,
            }
        )
        line._onchange_product_attribute_ids_configurator()
        self.assertIn(self.tax.id, line.tax_id.ids)

    def test_select_attribute_with_tax_fp_mapped(self):
        self.order.fiscal_position_id = self.fiscal_position
        line = self.env["sale.order.line"].new(
            {
                "order_id": self.order.id,
                "product_tmpl_id": self.product_template.id,
                "name": self.product_template.name,
                "product_uom_qty": 1,
                "product_uom": self.product_template.uom_id.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": self.product_template.id,
                            "attribute_id": self.attribute.id,
                            "value_id": self.attribute_value.id,
                            "owner_model": "sale.order.line",
                        },
                    )
                ],
                "create_product_variant": True,
            }
        )
        line._onchange_product_attribute_ids_configurator()
        self.assertIn(self.tax2.id, line.tax_id.ids)
