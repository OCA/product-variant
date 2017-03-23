# -*- coding: utf-8 -*-
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestStockPickingVariantMgmt(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingVariantMgmt, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test partner'})
        cls.attribute1 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 1',
            'value_ids': [
                (0, 0, {'name': 'Value 1'}),
                (0, 0, {'name': 'Value 2'}),
                (0, 0, {'name': 'Value 3'}),
                (0, 0, {'name': 'Value 4'}),
            ],
        })
        cls.product_tmpl = cls.env['product.template'].create({
            'name': 'Test template',
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': cls.attribute1.id,
                    'value_ids': [(6, 0, cls.attribute1.value_ids.ids)],
                }),
            ],
        })
        assert len(cls.product_tmpl.product_variant_ids) == 4
        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
        cls.picking_type = cls.env['stock.picking.type'].search([
            ('warehouse_id', '=', cls.warehouse.id),
            ('code', '=', 'incoming'),
        ], limit=1)
        cls.picking = cls.env['stock.picking'].create({
            'partner_id': cls.partner.id,
            'picking_type_id': cls.picking_type.id,
            'location_id': cls.partner.property_stock_supplier.id,
            'location_dest_id': cls.picking_type.default_location_dest_id.id,
        })
        cls.Move = cls.env['stock.move']
        cls.product1 = cls.product_tmpl.product_variant_ids[0]
        move_vals = cls.Move.onchange_product_id(
            prod_id=cls.product1.id,
            loc_id=cls.picking.location_id.id,
            loc_dest_id=cls.picking.location_dest_id.id,
            partner_id=cls.picking.partner_id.id,
        ).get('value', {})
        move_vals.update({
            'product_id': cls.product1.id,
            'picking_id': cls.picking.id,
            'product_uom_qty': 1,
        })
        cls.move1 = cls.Move.create(move_vals)
        cls.product2 = cls.product_tmpl.product_variant_ids[1]
        move_vals = cls.Move.onchange_product_id(
            prod_id=cls.product2.id,
            loc_id=cls.picking.location_id.id,
            loc_dest_id=cls.picking.location_dest_id.id,
            partner_id=cls.picking.partner_id.id,
        ).get('value', {})
        move_vals.update({
            'product_id': cls.product2.id,
            'picking_id': cls.picking.id,
            'product_uom_qty': 2,
        })
        cls.move2 = cls.Move.create(move_vals)
        cls.Wizard = cls.env['stock.manage.variant'].with_context(
            active_ids=cls.picking.ids, active_id=cls.picking.id,
            active_model=cls.picking._name,
        )
        cls.product_single = cls.env['product.product'].create({
            'name': 'Product without variants',
        })
        move_vals = cls.Move.onchange_product_id(
            prod_id=cls.product_single.id,
            loc_id=cls.picking.location_id.id,
            loc_dest_id=cls.picking.location_dest_id.id,
            partner_id=cls.picking.partner_id.id,
        ).get('value', {})
        move_vals.update({
            'product_id': cls.product_single.id,
            'picking_id': cls.picking.id,
            'product_uom_qty': 2,
        })
        cls.move3 = cls.Move.create(move_vals)

    def test_add_variants(self):
        self.move1.unlink()
        self.move2.unlink()
        self.move3.unlink()
        wizard = self.Wizard.new({'product_tmpl_id': self.product_tmpl.id})
        wizard._onchange_product_tmpl_id()
        wizard = wizard.create(wizard._convert_to_write(wizard._cache))
        self.assertEqual(len(wizard.variant_line_ids), 4)
        wizard.variant_line_ids[0].product_uom_qty = 1
        wizard.variant_line_ids[1].product_uom_qty = 2
        wizard.variant_line_ids[2].product_uom_qty = 3
        wizard.variant_line_ids[3].product_uom_qty = 4
        wizard.button_transfer_to_picking()
        self.assertEqual(len(self.picking.move_lines), 4,
                         "There should be 4 lines in the picking")
        self.assertEqual(self.picking.move_lines[0].product_uom_qty, 1)
        self.assertEqual(self.picking.move_lines[1].product_uom_qty, 2)
        self.assertEqual(self.picking.move_lines[2].product_uom_qty, 3)
        self.assertEqual(self.picking.move_lines[3].product_uom_qty, 4)

    def test_modify_variants(self):
        Wizard2 = self.Wizard.with_context(
            default_product_tmpl_id=self.product_tmpl.id,
            active_model='stock.move',
            active_id=self.move1.id, active_ids=self.move1.ids
        )
        wizard = Wizard2.create({})
        wizard._onchange_product_tmpl_id()
        self.assertEqual(
            len(wizard.variant_line_ids.filtered('product_uom_qty')), 2,
            "There should be two fields with any quantity in the wizard."
        )
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == self.product1).product_uom_qty = 0
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == self.product2).product_uom_qty = 10
        wizard.button_transfer_to_picking()
        self.assertFalse(self.move1.exists(), "Move not removed.")
        self.assertEqual(
            self.move2.product_uom_qty, 10, "Move not changed quantity.",
        )

    def test_variant_transfer(self):
        self.picking.action_confirm()
        self.picking.action_assign()
        self.assertEqual(len(self.picking.pack_operation_ids), 3)
        wizard = self.env['stock.transfer.manage.variant'].with_context(
            active_model='stock.picking', active_ids=self.picking.ids,
            active_id=self.picking.id,
        ).create({})
        self.assertEqual(len(wizard.variant_line_ids), 6)
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == self.product1
        ).qty_done = 1
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == self.product2
        ).qty_done = 2
        wizard.variant_line_ids.filtered(
            lambda x: x.product_id == self.product_single
        ).qty_done = 3
        wizard.button_transfer_to_picking()
        self.assertEqual(self.picking.pack_operation_ids.filtered(
            lambda x: x.product_id == self.product1
        ).qty_done, 1)
        self.assertEqual(self.picking.pack_operation_ids.filtered(
            lambda x: x.product_id == self.product2
        ).qty_done, 2)
        self.assertEqual(self.picking.pack_operation_ids.filtered(
            lambda x: x.product_id == self.product_single
        ).qty_done, 3)
