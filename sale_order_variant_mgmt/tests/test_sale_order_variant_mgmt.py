# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestSaleOrderVariantMgmt(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderVariantMgmt, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.attribute1 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 1',
            'value_ids': [
                (0, 0, {'name': 'Value 1'}),
                (0, 0, {'name': 'Value 2'}),
            ],
        })
        cls.attribute2 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 2',
            'value_ids': [
                (0, 0, {'name': 'Value X'}),
                (0, 0, {'name': 'Value Y'}),
            ],
        })
        cls.attribute3 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 3',
            'value_ids': [
                (0, 0, {'name': 'Value A'}),
                (0, 0, {'name': 'Value Z'}),
            ],
            'create_variant': 'no_variant',
        })
        cls.product_tmpl = cls.env['product.template'].create({
            'name': 'Test template',
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': cls.attribute1.id,
                    'value_ids': [(6, 0, cls.attribute1.value_ids.ids)],
                }),
                (0, 0, {
                    'attribute_id': cls.attribute2.id,
                    'value_ids': [(6, 0, cls.attribute2.value_ids.ids)],
                }),
                (0, 0, {
                    'attribute_id': cls.attribute3.id,
                    'value_ids': [(6, 0, cls.attribute3.value_ids.ids)],
                }),
            ],
        })
        assert len(cls.product_tmpl.product_variant_ids) == 4
        order = cls.env['sale.order'].new({'partner_id': cls.partner.id})
        order.onchange_partner_id()
        cls.order = order.create(order._convert_to_write(order._cache))
        cls.Wizard = cls.env['sale.manage.variant'].with_context(
            active_ids=cls.order.ids, active_id=cls.order.id,
            active_model=cls.order._name
        )
        cls.SaleOrderLine = cls.env['sale.order.line']

    def test_add_variants(self):
        wizard = self.Wizard.new({'product_tmpl_id': self.product_tmpl.id})
        wizard._onchange_product_tmpl_id()
        wizard = wizard.create(wizard._convert_to_write(wizard._cache))
        self.assertEqual(len(wizard.variant_line_ids), 4)
        wizard.variant_line_ids[0].product_uom_qty = 1
        wizard.variant_line_ids[1].product_uom_qty = 2
        wizard.variant_line_ids[2].product_uom_qty = 3
        wizard.variant_line_ids[3].product_uom_qty = 4
        wizard.button_transfer_to_order()
        self.assertEqual(len(self.order.order_line), 4,
                         "There should be 4 lines in the sale order")
        self.assertEqual(self.order.order_line[0].product_uom_qty, 1)
        self.assertEqual(self.order.order_line[1].product_uom_qty, 2)
        self.assertEqual(self.order.order_line[2].product_uom_qty, 3)
        self.assertEqual(self.order.order_line[3].product_uom_qty, 4)
        # Test template without variants
        tmpl = self.env['product.template'].create({'name': 'empty'})
        wizard.product_tmpl_id = tmpl.id
        wizard._onchange_product_tmpl_id()
        self.assertFalse(wizard.variant_line_ids)

    def test_modify_variants(self):
        # Disable one of the variants for covering that code part
        self.product_tmpl.product_variant_ids[-1].active = False
        product1 = self.product_tmpl.product_variant_ids[0]
        order_line1 = self.SaleOrderLine.new({
            'order_id': self.order.id,
            'product_id': product1.id,
            'product_uom_qty': 1,
        })
        order_line1.product_id_change()
        product2 = self.product_tmpl.product_variant_ids[1]
        order_line1 = self.SaleOrderLine.create(
            order_line1._convert_to_write(order_line1._cache))
        order_line2 = self.SaleOrderLine.new({
            'order_id': self.order.id,
            'product_id': product2.id,
            'product_uom_qty': 2,
        })
        order_line2.product_id_change()
        order_line2 = self.SaleOrderLine.create(
            order_line2._convert_to_write(order_line2._cache))
        Wizard2 = self.Wizard.with_context(
            default_product_tmpl_id=self.product_tmpl.id,
            active_model='sale.order.line',
            active_id=order_line1.id, active_ids=order_line1.ids
        )
        wizard = Wizard2.create({})
        wizard._onchange_product_tmpl_id()
        self.assertEqual(
            len(wizard.variant_line_ids.filtered('product_uom_qty')), 2,
            "There should be two fields with any quantity in the wizard."
        )
        wizard.variant_line_ids[0].product_uom_qty = 0
        wizard.variant_line_ids[1].product_uom_qty = 10
        wizard.button_transfer_to_order()
        self.assertFalse(order_line1.exists(), "Order line not removed.")
        self.assertEqual(
            order_line2.product_uom_qty, 10, "Order line not change quantity.")

    def test_partner_product_description(self):
        # Check if partner product name does not lose when a order line is
        # created
        variant = self.product_tmpl.product_variant_ids[0]
        self.env["product.supplierinfo"].create({
            'name': self.partner.id,
            'product_name': "Product name for partner",
            'product_id': variant.id,
            'product_tmpl_id': variant.product_tmpl_id.id
        })
        wizard = self.Wizard.new({'product_tmpl_id': self.product_tmpl.id})
        wizard._onchange_product_tmpl_id()
        wizard = wizard.create(wizard._convert_to_write(wizard._cache))
        wizard.variant_line_ids[0].product_uom_qty = 1
        wizard.button_transfer_to_order()
        self.assertIn(
            "Product name for partner", self.order.order_line[0].name)
