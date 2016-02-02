# -*- coding: utf-8 -*-
# © 2016 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestProuctVariantSalePrice(common.TransactionCase):

    def setUp(self):
        super(TestProuctVariantSalePrice, self).setUp()
        self.pricelist_model = self.env['product.pricelist']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.so_line_model = self.env['sale.order.line']
        self.partner = self.env.ref('base.res_partner_1')
        self.pricelist = self.env.ref('product_variant_sale_price.list1')

    def test_variant_lst_price(self):
        product_tmpl = self.product_tmpl_model.create(
            dict(name="Product template", list_price='121',))
        product = self.product_model.create(
            dict(product_tmpl_id=product_tmpl.id,
                 variant_lst_price='122.5'))
        res = self.so_line_model.product_id_change(
            self.pricelist.id, product.id, partner_id=self.partner.id)
        self.assertEqual(
            product.variant_lst_price, res['value']['price_unit'])
