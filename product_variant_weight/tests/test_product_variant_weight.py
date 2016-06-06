# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestProductVariantWeight(TransactionCase):

    def setUp(self):
        super(TestProductVariantWeight, self).setUp()
        self.template = self.env['product.template']
        self.product_template = self.template.create({
            'name': 'Product',
            'weight': 50,
            'weight_net': 50,
        })
        self.product = self.env.ref('product.product_product_4')

    def test_create_product_template(self):
        self.assertEqual(
            self.product_template.weight,
            self.product_template.product_variant_ids[:1].weight)
        self.assertEqual(
            self.product_template.weight_net,
            self.product_template.product_variant_ids[:1].weight_net)

    def test_update_variant(self):
        self.product.weight = 75
        self.product.weight_net = 75
        self.assertNotEqual(
            self.product.weight, self.product.product_tmpl_id.weight)
        self.assertNotEqual(
            self.product.weight_net, self.product.product_tmpl_id.weight_net)

    def test_update_template_variant(self):
        self.product.product_tmpl_id.weight = 200
        self.product.product_tmpl_id.weight_net = 200
        for variant in self.product.product_tmpl_id.product_variant_ids:
            self.assertEqual(self.product.weight, variant.weight)
            self.assertEqual(self.product.weight_net, variant.weight_net)
