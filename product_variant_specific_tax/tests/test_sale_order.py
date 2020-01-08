# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleOrder(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()
        cls.product_product = cls.env['product.product']
        cls.sale_order = cls.env['sale.order']
        cls.sale_order_line = cls.env['sale.order.line']
        cls.product_template = cls.env['product.template']
        cls.res_partner = cls.env['res.partner']
        cls.account_tax = cls.env['account.tax']

        cls.account_tax_std = cls.account_tax.create({
            'name': 'Standard Tax',
            'amount': 5.0,
        })
        cls.account_tax_recycling = cls.account_tax.create({
            'name': 'Recycling Tax',
            'amount_type': 'fixed',
            'amount': 10.0,
        })

        cls.customer = cls.res_partner.create({
            'name': 'Customer 1',
        })

        cls.product_template_1 = cls.product_template.create({
            'name': 'Product template 1',
            'list_price': 100,
            'description_sale': 'Template description',
            'taxes_id': [(6, 0, [cls.account_tax_std.id])]
        })

        cls.product_product_without = cls.product_product.create({
            'product_tmpl_id': cls.product_template_1.id
        })
        cls.product_product_with = cls.product_product_without.copy({
            'additional_tax_ids': [(6, 0, [cls.account_tax_recycling.id])],
        })

    def test_onchange_product_id(self):
        sale = self.sale_order.create({'partner_id': self.customer.id})
        line = self.sale_order_line.create({
            'order_id': sale.id,
            'product_id': self.product_product_without.id,
            'price_unit': 100,
            'product_uom': self.product_template_1.uom_id.id,
            'product_uom_qty': 1,
        })

        line.product_id_change()
        self.assertEquals(line.tax_id, self.account_tax_std)

        line.product_id = self.product_product_with
        line.product_id_change()
        self.assertEquals(
            line.tax_id,
            self.account_tax_std | self.account_tax_recycling
        )

        line.product_id = self.product_product_without
        line.product_id_change()
        self.assertEquals(line.tax_id, self.account_tax_std)
