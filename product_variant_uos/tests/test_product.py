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
        self.product_uom_kgm = self.env.ref('product.product_uom_kgm')
        self.product_uom_gram = self.env.ref('product.product_uom_gram')
        return result

    def test_product(self):

        # writing 5 kg to template
        self.product_product_4_product_template.uos_coeff = 5
        self.assertEqual(self.product_product_4_product_template.uos_coeff, 5)
        self.assertEqual(self.product_product_4.uos_coeff, 5)
        self.assertEqual(self.product_product_4b.uos_coeff, 5)

        self.product_product_4_product_template.uos_id = (
            self.product_uom_kgm.id)
        self.assertEqual(
            self.product_product_4_product_template.uos_id.id,
            self.product_uom_kgm.id)
        self.assertEqual(
            self.product_product_4.uos_id.id, self.product_uom_kgm.id)
        self.assertEqual(
            self.product_product_4b.uos_id.id, self.product_uom_kgm.id)

        # writing values to variants
        self.product_product_4.uos_coeff = 6
        self.product_product_4b.uos_coeff = 7
        self.assertEqual(self.product_product_4_product_template.uos_coeff, 5)
        self.assertEqual(self.product_product_4.uos_coeff, 6)
        self.assertEqual(self.product_product_4b.uos_coeff, 7)

        self.product_product_4.uos_id = self.product_uom_gram.id
        self.assertEqual(
            self.product_product_4_product_template.uos_id.id,
            self.product_uom_kgm.id)
        self.assertEqual(
            self.product_product_4.uos_id.id, self.product_uom_gram.id)
        self.assertEqual(
            self.product_product_4b.uos_id.id, self.product_uom_kgm.id)

        # writing template
        self.product_product_4_product_template.uos_coeff = 8
        self.assertEqual(self.product_product_4_product_template.uos_coeff, 8)
        self.assertEqual(self.product_product_4.uos_coeff, 8)
        self.assertEqual(self.product_product_4b.uos_coeff, 8)

        self.product_product_4_product_template.uos_id = (
            self.product_uom_kgm.id)
        self.assertEqual(
            self.product_product_4.uos_id.id, self.product_uom_kgm.id)
        self.assertEqual(
            self.product_product_4b.uos_id.id, self.product_uom_kgm.id)
