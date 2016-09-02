# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase


class TestProcurement(TransactionCase):

    # Test if the supplier configured on the product is the supplier used
    # for the automatic purchase order generated when runing the procurement

    def test_confirm_procurement_with_tmpl_supplier(self):
        proc = self.env.ref(
            'product_variant_supplierinfo.procurement_1')
        partner_1 = self.env.ref('base.res_partner_1')
        proc.run()
        self.assertEqual(proc.purchase_id.partner_id.id, partner_1.id)

    def test_confirm_procurement_with_variant_supplier(self):
        proc = self.env.ref(
            'product_variant_supplierinfo.procurement_2')
        partner = self.env.ref('base.res_partner_2')
        proc.run()
        self.assertEqual(proc.purchase_id.partner_id.id, partner.id)
