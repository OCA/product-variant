# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestProductProduct(TransactionCase):

    def test_get_selection_cost_method(self):
        self.env['product.product']._get_selection_cost_method()

    def test_default_cost_method(self):
        product = self.env['product.product'].create({'name': 'Test 01'})
        template = self.env['product.template'].create({'name': 'Test 02'})
        self.assertEqual(product.cost_method, template.cost_method)

    def test_product_price_history(self):
        price_history_obj = self.env['product.price.history']
        product_obj = self.env['product.product']
        product = product_obj.create({'name': 'Test create',
                                      'standard_price': 15.00})
        history = price_history_obj.search([('product_id', '=', product.id)])
        self.assertEqual(product.standard_price, history.cost)
        product.standard_price = 25.00
        history = price_history_obj.search([('product_id', '=', product.id)])
        self.assertEqual(len(history), 2)

    def test_product_variant_cost_prices(self):
        product_obj = self.env['product.product']
        template_obj = self.env['product.template']
        template = template_obj.create({'name': 'Test template',
                                        'standard_price': 5})
        product_1 = product_obj.create({'name': 'Product 01',
                                        'product_tmpl_id': template.id,
                                        'standard_price': 10})
        product_2 = product_obj.create({'name': 'Product 02',
                                        'product_tmpl_id': template.id,
                                        'standard_price': 20})
        product_3 = product_obj.create({'name': 'Product 03',
                                        'product_tmpl_id': template.id,
                                        'standard_price': 30})
        self.assertEqual(template.standard_price, 5)
        self.assertEqual(product_1.standard_price, 10)
        self.assertEqual(product_2.standard_price, 20)
        self.assertEqual(product_3.standard_price, 30)
