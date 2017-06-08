# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestProductVariants(common.TransactionCase):

    def setUp(self):
        super(TestProductVariants, self).setUp()
        self.product_tmpl_model = self.env['product.template']
        self.product_categ_model = self.env['product.category']

    def test_no_variant_creation(self):
        prod_tmpl = self.product_tmpl_model.create({
            'name': 'ProductTemplate4Test',
            'no_create_variants': 'yes',
            'attribute_line_ids': [
                (4, self.env.ref('product.product_attribute_line_1').id)]
        })
        self.assertFalse(prod_tmpl.product_variant_ids)

    def test_with_variant_creation(self):
        prod_tmpl = self.product_tmpl_model.create({
            'name': 'ProductTemplate4Test',
            'no_create_variants': 'no',
            'attribute_line_ids': [
                (4, self.env.ref('product.product_attribute_line_1').id)]
        })
        self.assertTrue(prod_tmpl.product_variant_ids)

    def test_category_no_variant_creation(self):
        product_categ = self.product_categ_model.create({
            'name': 'ProductCategory4Test',
            'no_create_variants': True,
        })
        prod_tmpl = self.product_tmpl_model.create({
            'name': 'ProductTemplate4Test',
            'no_create_variants': 'empty',
            'categ_id': product_categ.id,
            'attribute_line_ids': [
                (4, self.env.ref('product.product_attribute_line_1').id)]
        })
        self.assertFalse(prod_tmpl.product_variant_ids)

    def test_category_with_variant_creation(self):
        product_categ = self.product_categ_model.create({
            'name': 'ProductCategory4Test',
            'no_create_variants': False,
        })
        prod_tmpl = self.product_tmpl_model.create({
            'name': 'ProductTemplate4Test',
            'no_create_variants': 'empty',
            'categ_id': product_categ.id,
            'attribute_line_ids': [
                (4, self.env.ref('product.product_attribute_line_1').id)]
        })
        self.assertTrue(prod_tmpl.product_variant_ids)
