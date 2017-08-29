# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class ProductVariantTemplateData(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(ProductVariantTemplateData, self).setUp(
            *args, **kwargs)
        # template
        self.template_model = self.env['product.template']
        self.product_template = self.template_model.create({
            'name': 'Product Template',
            'sale_delay': 8.0,
        })
        # variants
        self.product_model = self.env['product.product']
        self.product_1 = self.product_model.create({
            'product_tmpl_id': self.product_template.id,
        })
        self.product_2 = self.product_model.create({
            'product_tmpl_id': self.product_template.id,
        })
        return result

    def test_post_init_hook(self):
        from ..hooks import post_init_hook
        # case where post_init_hook is applied
        post_init_hook(self.cr, None)
        self.product_template.product_variant_ids.invalidate_cache()
        self.assertEqual(
            self.product_template.sale_delay,
            self.product_1.sale_delay)
        self.assertEqual(
            self.product_template.sale_delay,
            self.product_2.sale_delay)
        # case where post_init_hook is not applied
        self.product_template.product_variant_ids.write({
            'sale_delay': 9.0,
        })
        post_init_hook(self.cr, None)
        self.product_template.product_variant_ids.invalidate_cache()
        self.assertEqual(self.product_template.sale_delay, 8.0)
        self.assertEqual(self.product_1.sale_delay, 9.0)
        self.assertEqual(self.product_2.sale_delay, 9.0)

    def test_create_product_template(self):
        new_template = self.template_model.create({
            'name': 'New Product Template',
            'sale_delay': 5.0,
        })
        self.assertEqual(
            new_template.sale_delay,
            new_template.product_variant_ids.sale_delay)

    def test_create_variant(self):
        new_variant = self.product_model.create({
            'product_tmpl_id': self.product_template.id,
        })
        self.assertEqual(
            self.product_template.sale_delay,
            new_variant.sale_delay)

    def test_update_variant(self):
        self.product_1.sale_delay = 5.0
        self.assertNotEqual(
            self.product_1.sale_delay,
            self.product_1.product_tmpl_id.sale_delay)

    def test_update_template_variant(self):
        self.product_1.product_tmpl_id.sale_delay = 5.0
        self.product_1.product_tmpl_id.weight = 50.0
        for variant in self.product_1.product_tmpl_id.product_variant_ids:
            self.assertEqual(
                self.product_1.sale_delay, variant.sale_delay)
