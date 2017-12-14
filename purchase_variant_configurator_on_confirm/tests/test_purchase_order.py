# -*- coding: utf-8 -*-
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


class TestPurchaseOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()
        cls.product_attribute_value = cls.env['product.attribute.value']
        cls.product_template = cls.env['product.template'].with_context(
            check_variant_creation=True,
        )
        cls.category1 = cls.env['product.category'].create({
            'name': 'No create variants category',
        })
        cls.attribute1 = cls.env['product.attribute'].create({
            'name': 'Test Attribute 1',
        })
        cls.value1 = cls.product_attribute_value.create({
            'name': 'Value 1',
            'attribute_id': cls.attribute1.id,
        })
        cls.value2 = cls.product_attribute_value.create({
            'name': 'Value 2',
            'attribute_id': cls.attribute1.id,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier 1',
            'is_company': True,
            'supplier': True,
        })
        cls.template_name = 'Product template 1'
        cls.product_template_yes = cls.product_template.create({
            'name': cls.template_name,
            'no_create_variants': 'yes',
            'categ_id': cls.category1.id,
            'standard_price': 100,
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': cls.attribute1.id,
                    'value_ids': [(6, 0, [cls.value1.id, cls.value2.id])],
                }),
            ],
            'seller_ids': [
                (0, 0, {
                    'name': cls.supplier.id,
                    'min_qty': 10,
                    'price': 90,
                })
            ]
        })
        cls.product_template_no = cls.product_template.create({
            'name': 'Product template 2',
            'categ_id': cls.category1.id,
            'no_create_variants': 'no',
            'description_purchase': "Purchase Description"
        })
        cls.order = cls.env['purchase.order'].create({
            'partner_id': cls.supplier.id,
        })

    def test_onchange_product_tmpl_id(self):
        line = self.env['purchase.order.line'].new({
            'order_id': self.order.id,
            'product_tmpl_id': self.product_template_yes.id,
        })
        line._onchange_product_tmpl_id_configurator()
        self.assertEqual(line.name, self.template_name)
        self.assertEqual(line.product_uom, self.product_template_yes.uom_id)
        self.assertEqual(line.price_unit, 90)
        self.assertEqual(line.product_qty, 10)
        self.assertTrue(line.date_planned)

    def test_button_confirm(self):
        line1 = self.env['purchase.order.line'].new({
            'order_id': self.order.id,
            'product_tmpl_id': self.product_template_yes.id,
        })
        line1._onchange_product_tmpl_id_configurator()
        line1.product_attribute_ids[0].value_id = self.value1.id
        line1 = line1.create(line1._convert_to_write(line1._cache))
        self.order.button_confirm()
        self.assertTrue(line1.product_id)
        line2 = self.env['purchase.order.line'].new({
            'order_id': self.order.id,
            'product_tmpl_id': self.product_template_yes.id,
        })
        line2._onchange_product_tmpl_id_configurator()
        line2.product_attribute_ids[0].value_id = self.value1.id
        line2 = line2.create(line2._convert_to_write(line2._cache))
        self.assertTrue(line2.product_id)

    def test_copy(self):
        line1 = self.env['purchase.order.line'].new({
            'order_id': self.order.id,
            'product_tmpl_id': self.product_template_yes.id,
        })
        line1._onchange_product_tmpl_id_configurator()
        line1.product_attribute_ids[0].value_id = self.value1.id
        old_date = '2017-01-01'
        line1.date_planned = old_date
        line1.create(line1._convert_to_write(line1._cache))
        new_order = self.order.copy()
        self.assertNotEqual(new_order.order_line.date_planned, old_date)
