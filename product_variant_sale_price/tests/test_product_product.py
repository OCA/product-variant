# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestProductProduct(TransactionCase):

    def setUp(self):
        super(TestProductProduct, self).setUp()
        self.template_model = self.env['product.template']
        self.product_model = self.env['product.product']
