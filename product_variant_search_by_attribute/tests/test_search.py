# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestSearchByAttribute(TransactionCase):
    def test_attribute_str(self):
        self.assertEqual(self.ipod16.attribute_str, '16 gb')

    def test_change_attribute_value(self):
        self.attrib16.write({'name': '16 GBsuffix'})
        self.assertEqual(self.ipod16.attribute_str, '16 gbsuffix')

    def test_no_record_returned_by_search(self):
        res = self.product_m.search([('attribute_str', 'ilike', '16 32')])
        self.assertEqual(len(res), 0)

    def test_one_record_returned_by_search(self):
        res = self.product_m.search([('attribute_str', 'ilike', '16 blac')])
        self.assertEqual(len(res), 1)

    def setUp(self):
        super(TestSearchByAttribute, self).setUp()
        self.product_m = self.env['product.product']
        self.ipod16 = self.env.ref('product.product_product_11')
        self.attrib16 = self.env.ref('product.product_attribute_value_1')
