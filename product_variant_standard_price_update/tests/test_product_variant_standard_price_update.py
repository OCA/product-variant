# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class TestProductVariantStandardPriceUpdate(common.SavepointCase):

    @classmethod
    def setUpClass(self):
        super(TestProductVariantStandardPriceUpdate, self).setUpClass()
        self.ProductTemplate = self.env['product.template']
        self.product_template = self.ProductTemplate.create({
            'name': 'Product - template - Test',
            'standard_price': 100.00,
        })
        self.attribute = self.env['product.attribute'].create({
            'name': 'Test Attribute',
        })
        self.value1 = self.env['product.attribute.value'].create({
            'name': 'Value 1',
            'attribute_id': self.attribute.id,
        })
        self.value2 = self.env['product.attribute.value'].create({
            'name': 'Value 2',
            'attribute_id': self.attribute.id,
        })
        self.product_template_var = self.ProductTemplate.create({
            'name': 'Product - template - Test',
            'standard_price': 100.00,
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': self.attribute.id,
                    'value_ids': [(6, 0, [self.value1.id, self.value2.id])]
                })],
        })

    def test_update_template_standard_price(self):
        self.product_template.standard_price = 150.00
        self.assertTrue(self.product_template.same_cost_variants)
        self.assertEquals(self.product_template.standard_price, 150.00)

    def test_update_variant_standard_price(self):
        variant = self.product_template_var.product_variant_ids[0]
        variant.standard_price = 150.00
        self.assertFalse(self.product_template_var.same_cost_variants)
        self.assertEquals(self.product_template_var.standard_price, 100.00)

    def test_update_simple_product_standard_price(self):
        self.product_template.standard_price = 300.00
        self.assertTrue(self.product_template.same_cost_variants)
        self.assertEquals(self.product_template.standard_price, 300.00)
