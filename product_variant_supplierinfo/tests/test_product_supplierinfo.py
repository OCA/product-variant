# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestProductProduct(TransactionCase):

    def setUp(self):
        super(TestProductProduct, self).setUp()

        self.product = self.env.ref('product.product_product_4')
        self.supplierinfo_obj = self.env['product.supplierinfo']
        self.supplier = self.env.ref('base.res_partner_1')

    def test_create_product(self):
        vals = {
            'name': self.supplier.id,
            'product_id': self.product.id,
        }
        supplierinfo = self.supplierinfo_obj.create(vals)
        self.assertEqual(
            supplierinfo.product_tmpl_id.id, self.product.product_tmpl_id.id)

        vals = {
            'name': self.supplier.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
        }
        supplierinfo.write(vals)
        self.assertEqual(supplierinfo.product_id.id, self.product.id)
