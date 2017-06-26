# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
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

        # writing loc_rack to template
        self.product_product_4_product_template.loc_rack = 'A'
        self.assertEqual(self.product_product_4_product_template.loc_rack, 'A')
        self.assertEqual(self.product_product_4.loc_rack, 'A')
        self.assertEqual(self.product_product_4b.loc_rack, 'A')

        # writing values to variants
        self.product_product_4.loc_rack = 'B'
        self.product_product_4b.loc_rack = 'B'
        self.assertEqual(self.product_product_4_product_template.loc_rack, 'A')
        self.assertEqual(self.product_product_4.loc_rack, 'B')
        self.assertEqual(self.product_product_4b.loc_rack, 'B')

        # writing loc_row to template
        self.product_product_4_product_template.loc_row = '1'
        self.assertEqual(self.product_product_4_product_template.loc_row, '1')
        self.assertEqual(self.product_product_4.loc_row, '1')
        self.assertEqual(self.product_product_4b.loc_row, '1')

        # writing values to variants
        self.product_product_4.loc_row = '2'
        self.product_product_4b.loc_row = '2'
        self.assertEqual(self.product_product_4_product_template.loc_row, '1')
        self.assertEqual(self.product_product_4.loc_row, '2')
        self.assertEqual(self.product_product_4b.loc_row, '2')

        # writing loc_case to template
        self.product_product_4_product_template.loc_case = 'C'
        self.assertEqual(self.product_product_4_product_template.loc_case, 'C')
        self.assertEqual(self.product_product_4.loc_case, 'C')
        self.assertEqual(self.product_product_4b.loc_case, 'C')

        # writing values to variants
        self.product_product_4.loc_case = 'D'
        self.product_product_4b.loc_case = 'D'
        self.assertEqual(self.product_product_4_product_template.loc_case, 'C')
        self.assertEqual(self.product_product_4.loc_case, 'D')
        self.assertEqual(self.product_product_4b.loc_case, 'D')
