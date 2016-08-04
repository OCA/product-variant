# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestSearchByAttribute(TransactionCase):
    def test_change_attribute_value(self):
        self.attrib16.write({'name': '16 GBsuffix'})
        self.assertEqual(self.ipod16.attribute_str, '16 GBsuffix')

    def setUp(self):
        super(TestSearchByAttribute, self).setUp()
        # self.prd_m = self.env['product.product']
        self.ipod16 = self.env.ref('product.product_product_11')
        self.attrib16 = self.env.ref('product.product_attribute_value_1')
