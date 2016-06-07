# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestProductVariantWeight(TransactionCase):

    def setUp(self):
        super(TestProductVariantWeight, self).setUp()
        self.template = self.env['product.template']
        self.product_product = self.env['product.product']

        self.product_template = self.template.create({
            'name': 'Product Template',
            'weight': 50,
            'weight_net': 50,
        })

        self.product = self.product_product.create({
            'product_tmpl_id': self.product_template.id,
            'name_template': 'Product Template',
        })
        self.product_1 = self.product_product.create({
            'product_tmpl_id': self.product_template.id
        })

    def test_post_init_hook(self):
        from ..hooks import post_init_hook
        self.product_template.product_variant_ids.write({
            'weight': 0.0,
            'weight_net': 0.0,
        })
        post_init_hook(self.cr, None)
        self.product_template.product_variant_ids.invalidate_cache()
        self.assertEqual(
            self.product_template.weight, self.product.weight)
        self.assertEqual(
            self.product_template.weight_net, self.product.weight_net)
        self.assertEqual(
            self.product_template.weight, self.product_1.weight)
        self.assertEqual(
            self.product_template.weight_net, self.product_1.weight_net)

    def test_create_product_template(self):
        self.assertEqual(
            self.product_template.weight,
            self.product_template.product_variant_ids[:1].weight)
        self.assertEqual(
            self.product_template.weight_net,
            self.product_template.product_variant_ids[:1].weight_net)

    def test_create_variant(self):
        new_variant = self.product_product.create({
            'product_tmpl_id': self.product_template.id
        })
        self.assertEqual(self.product_template.weight, new_variant.weight)
        self.assertEqual(
            self.product_template.weight_net, new_variant.weight_net)

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
