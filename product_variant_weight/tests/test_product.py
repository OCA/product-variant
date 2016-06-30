# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class Product(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(Product, self).setUp(*args, **kwargs)
        # template
        self.product_product_4_product_template = self.env.ref(
            'product.product_product_4_product_template')
        # variants
        self.product_product_4 = self.env.ref('product.product_product_4')
        self.product_product_4b = self.env.ref('product.product_product_4b')
        return result

    def test_product(self):

        # writing 5 to template
        self.product_product_4_product_template.weight = 5
        self.assertEqual(self.product_product_4_product_template.weight, 5)
        self.assertEqual(self.product_product_4.weight, 5)
        self.assertEqual(self.product_product_4b.weight, 5)

        # writing values to variants
        self.product_product_4.weight = 6
        self.product_product_4b.weight = 7
        self.assertEqual(self.product_product_4_product_template.weight, 5)
        self.assertEqual(self.product_product_4.weight, 6)
        self.assertEqual(self.product_product_4b.weight, 7)

        # writing 8 to template
        self.product_product_4_product_template.weight = 8
        self.assertEqual(self.product_product_4_product_template.weight, 8)
        self.assertEqual(self.product_product_4.weight, 8)
        self.assertEqual(self.product_product_4b.weight, 8)
