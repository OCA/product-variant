# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase


class TestProductVariantPrice(TransactionCase):
    def setUp(self):
        super().setUp()
        self.template = self.env["product.template"]
        self.product_product = self.env["product.product"]
        self.attribute = self.env["product.attribute"]
        self.attribute_value = self.env["product.attribute.value"]

        self.att_color = self.attribute.create({"name": "color_test"})

        self.att_color_blue = self.attribute_value.create(
            {"name": "Blue", "attribute_id": self.att_color.id}
        )
        self.att_color_red = self.attribute_value.create(
            {"name": "Red", "attribute_id": self.att_color.id}
        )

        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_dozen = self.ref("uom.product_uom_dozen")

        self.product_template = self.template.create(
            {
                "name": "Product Template",
                "list_price": 1500.00,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.att_color.id,
                            "value_ids": [
                                (6, 0, (self.att_color_blue + self.att_color_red).ids)
                            ],
                        },
                    )
                ],
                "uom_id": self.uom_unit.id,
            }
        )

        self.product_blue = self.product_template.product_variant_ids.filtered(
            lambda x: x.product_template_attribute_value_ids.product_attribute_value_id
            == self.att_color_blue
        )
        self.product_red = self.product_template.product_variant_ids.filtered(
            lambda x: x.product_template_attribute_value_ids.product_attribute_value_id
            == self.att_color_red
        )

    def test_post_init_hook(self):
        from ..hooks import set_sale_price_on_variant

        self.product_template.product_variant_ids.write({"fix_price": 0.0})
        # Take account price extra
        self.product_blue.product_template_attribute_value_ids.write(
            {"price_extra": 100.00}
        )
        self.product_red.product_template_attribute_value_ids.write(
            {"price_extra": 200.00}
        )

        # Flush the records to DB before direct SQL
        self.product_blue.flush()
        self.product_red.flush()

        set_sale_price_on_variant(self.cr, None, self.product_template.id)
        self.product_template.product_variant_ids.invalidate_cache()
        self.assertEqual(
            self.product_template.list_price + 100.00, self.product_blue.lst_price
        )
        self.assertEqual(
            self.product_template.list_price + 200.00, self.product_red.lst_price
        )

    def test_create_product_template(self):
        self.assertEqual(
            self.product_template.list_price,
            self.product_template.product_variant_ids[:1].lst_price,
        )

    def test_create_product_template_different_uom(self):
        new_template = self.product_template.with_context(uom=self.uom_dozen).copy(
            {"uom_id": self.uom_dozen}
        )
        self.assertEqual(
            new_template.list_price, new_template.product_variant_ids[:1].lst_price
        )

    def test_create_variant(self):
        new_variant = self.product_product.create(
            {"product_tmpl_id": self.product_template.id}
        )
        self.assertEqual(self.product_template.list_price, new_variant.lst_price)

    def test_create_variant_different_uom(self):
        new_variant = self.product_product.with_context(uom=self.uom_dozen).create(
            {"product_tmpl_id": self.product_template.id, "uom_id": self.uom_dozen}
        )
        self.assertEqual(self.product_template.list_price, new_variant.lst_price)

    def test_update_variant(self):
        self.product_blue.lst_price = 2000.00
        self.assertNotEqual(
            self.product_blue.lst_price, self.product_blue.product_tmpl_id.list_price
        )
        self.assertEqual(self.product_blue.lst_price, self.product_blue.fix_price)
        # to check skip_update_fix_price
        self.assertNotEqual(self.product_blue.lst_price, self.product_red.lst_price)
        self.assertEqual(self.product_red.lst_price, 1500.00)

    def test_update_variant_different_uom(self):
        self.product_blue.write({"uom_id": self.uom_dozen})
        self.product_blue.with_context(uom=self.uom_dozen).lst_price = 2000.00
        self.assertEqual(self.product_blue.lst_price, self.product_blue.fix_price)

    def test_update_variant_no_multiple(self):
        self.product_red.unlink()
        self.product_blue.lst_price = 2000.00
        self.assertEqual(self.product_blue.lst_price, self.product_blue.fix_price)

    def test_update_template_variant(self):
        self.product_blue.product_tmpl_id.list_price = 200
        for variant in self.product_blue.product_tmpl_id.product_variant_ids:
            self.assertEqual(self.product_blue.list_price, variant.lst_price)
