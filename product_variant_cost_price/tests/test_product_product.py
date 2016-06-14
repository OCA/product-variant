# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Javier Iniesta
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestProductProduct(TransactionCase):

    def setUp(self):
        super(TestProductProduct, self).setUp()
        self.template_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.attribute = self.env['product.attribute'].create(
            {'name': 'Test attribute'})
        self.value1 = self.env['product.attribute.value'].create(
            {'name': 'Test value 1',
             'attribute_id': self.attribute.id})
        self.value2 = self.env['product.attribute.value'].create(
            {'name': 'Test value 2',
             'attribute_id': self.attribute.id})
        self.product = self.product_model.create(
            {'name': 'Product',
             'standard_price': 15})
        self.template_single = self.template_model.create(
            {'name': 'Template',
             'attribute_line_ids': [
                 [0, 0, {'attribute_id': self.attribute.id,
                         'value_ids': [[6, 0, [self.value1.id]]]}]]})
        self.product_single = self.template_single.product_variant_ids[0]
        self.template_multi = self.template_model.create(
            {'name': 'Template multi',
             'standard_price': 5})
        self.product_multi_1 = self.product_model.create(
            {'name': 'Product 01',
             'product_tmpl_id': self.template_multi.id,
             'standard_price': 10})
        self.product_multi_2 = self.product_model.create(
            {'name': 'Product 02',
             'product_tmpl_id': self.template_multi.id,
             'standard_price': 20})
        self.product_multi_3 = self.product_model.create(
            {'name': 'Product 03',
             'product_tmpl_id': self.template_multi.id,
             'standard_price': 30})

    def test_default_cost_method(self):
        self.assertEqual(
            self.product.cost_method, self.template_single.cost_method)

    def test_propagate_cost(self):
        # From product to template
        self.product_single.standard_price = 100
        self.assertEqual(self.template_single.standard_price, 100)
        prev_price = self.template_multi.standard_price
        self.product_multi_1.standard_price = 100
        self.assertEqual(self.template_multi.standard_price, prev_price)
        # From template to product
        self.template_multi.standard_price = 100

    def test_product_price_history(self):
        price_history_obj = self.env['product.price.history.product']
        history = price_history_obj.search(
            [('product_id', '=', self.product.id)])
        self.assertEqual(self.product.standard_price, history.cost)
        self.product.standard_price = 25.00
        history = price_history_obj.search(
            [('product_id', '=', self.product.id)])
        self.assertEqual(len(history), 2)

    def test_product_template_price_history(self):
        price_history_obj = self.env['product.price.history']
        variant_history_obj = self.env['product.price.history.product']
        history = price_history_obj.search(
            [('product_template_id', '=', self.template_single.id)])
        variant_history = variant_history_obj.search(
            [('product_id', '=', self.product_single.id)])
        self.assertEqual(len(history), 1)
        self.assertEqual(len(variant_history), 1)
        self.assertEqual(self.template_single.standard_price, history.cost)
        self.template_single.standard_price = 20.00
        history = price_history_obj.search(
            [('product_template_id', '=', self.template_single.id)])
        variant_history = variant_history_obj.search(
            [('product_id', '=', self.product_single.id)])
        self.assertEqual(self.product_single.standard_price,
                         self.template_single.standard_price)
        self.assertEqual(len(history), 2)
        self.assertEqual(len(variant_history), 2)

    def test_product_variant_cost_prices(self):
        self.assertEqual(self.template_multi.standard_price, 5)
        self.assertEqual(self.product_multi_1.standard_price, 10)
        self.assertEqual(self.product_multi_2.standard_price, 20)
        self.assertEqual(self.product_multi_3.standard_price, 30)

    def test_new_variant_creation_prices(self):
        price_history_obj = self.env['product.price.history']
        variant_history_obj = self.env['product.price.history.product']
        self.template_single.write(
            {'attribute_line_ids': [
                [1, self.template_single.attribute_line_ids[:1].id,
                 {'value_ids': [[6, 0, [self.value1.id, self.value2.id]]]}]]})
        history = price_history_obj.search(
            [('product_template_id', '=', self.template_single.id)])
        self.assertEqual(len(history), 1)
        for product in self.template_single.product_variant_ids:
            variant_history = variant_history_obj.search(
                [('product_id', '=', product.id)])
            self.assertEqual(len(variant_history), 1)
            self.assertEqual(self.template_single.standard_price,
                             product.standard_price)
