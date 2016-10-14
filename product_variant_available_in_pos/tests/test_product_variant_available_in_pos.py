# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class ProductVariantAvailableInPos(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(ProductVariantAvailableInPos, self).setUp(
            *args, **kwargs)
        # template
        self.template_model = self.env['product.template']
        self.product_template = self.template_model.create({
            'name': 'Product Template',
            'available_in_pos': True,
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
        self.product_template.product_variant_ids.write({
            'available_in_pos': False,
        })
        post_init_hook(self.cr, None)
        self.product_template.product_variant_ids.invalidate_cache()
        self.assertEqual(
            self.product_template.available_in_pos,
            self.product_1.available_in_pos)
        self.assertEqual(
            self.product_template.available_in_pos,
            self.product_2.available_in_pos)

    def test_create_product_template(self):
        new_template = self.template_model.create({
            'name': 'New Product Template',
            'available_in_pos': True,
        })
        self.assertEqual(
            new_template.available_in_pos,
            new_template.product_variant_ids.available_in_pos)

    def test_create_variant(self):
        new_variant = self.product_model.create({
            'product_tmpl_id': self.product_template.id,
        })
        self.assertEqual(
            self.product_template.available_in_pos,
            new_variant.available_in_pos)

    def test_update_variant(self):
        self.product_1.available_in_pos = False
        self.assertNotEqual(
            self.product_1.available_in_pos,
            self.product_1.product_tmpl_id.available_in_pos)

    def test_update_template_variant(self):
        self.product_1.product_tmpl_id.available_in_pos = False
        for variant in self.product_1.product_tmpl_id.product_variant_ids:
            self.assertEqual(
                self.product_1.available_in_pos, variant.available_in_pos)
