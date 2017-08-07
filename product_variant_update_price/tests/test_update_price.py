# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase


class TestUpdatePrice(TransactionCase):

    def test_ipad_increase_10_percent(self):
        ipad = self.env.ref(
            'product.product_product_4_product_template')
        ipad16wh = self.env.ref('product.product_product_4')
        ipad32wh = self.env.ref('product.product_product_4c')
        self.assertEqual(ipad16wh.lst_price, 750.0,
                         "Demo data changed for ipad 16")
        self.assertEqual(ipad32wh.lst_price, 800.4,
                         "Demo data changed for ipad 32")
        wiz_obj = self.env['product.update.price'].create({'percentage': 10})
        wiz_obj.with_context(active_ids=[ipad.id]).update_price()
        self.assertEqual(ipad16wh.lst_price, 825.0,
                         "Price should be 825.0 instead of %s"
                         % ipad16wh.lst_price)
        self.assertEqual(ipad32wh.lst_price, 880.44,
                         "Price should be 880.44 instead of %s"
                         % ipad32wh.lst_price)
