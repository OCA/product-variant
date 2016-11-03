# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import SavepointCase


class TestPurchaseOrder(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrder, cls).setUpClass()

        # ENVIRONMENTS
        cls.product_attribute = cls.env['product.attribute']
        cls.product_attribute_value = cls.env['product.attribute.value']
        cls.product_template = cls.env['product.template'].with_context(
            check_variant_creation=True)
        cls.purchase_order = cls.env['purchase.order']
        cls.product_product = cls.env['product.product']
        cls.purchase_order_line = cls.env['purchase.order.line']
        cls.res_partner = cls.env['res.partner']
        cls.product_category = cls.env['product.category']

        # Instances: product category
        cls.category1 = cls.product_category.create({
            'name': 'No create variants category',
        })

        # Instances: product attribute
        cls.attribute1 = cls.product_attribute.create({
            'name': 'Test Attribute 1',
        })

        # Instances: product attribute value
        cls.value1 = cls.product_attribute_value.create({
            'name': 'Value 1',
            'attribute_id': cls.attribute1.id,
        })
        cls.value2 = cls.product_attribute_value.create({
            'name': 'Value 2',
            'attribute_id': cls.attribute1.id,
        })

        # Instances: product template
        cls.product_template_yes = cls.product_template.create({
            'name': 'Product template 1',
            'no_create_variants': 'yes',
            'categ_id': cls.category1.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attribute1.id,
                        'value_ids': [(6, 0, [cls.value1.id,
                                              cls.value2.id])]})],
        })

        cls.product_template_no = cls.product_template.create({
            'name': 'Product template 2',
            'categ_id': cls.category1.id,
            'no_create_variants': 'no',
            'description_purchase': "Purchase Description"
        })

        cls.supplier = cls.res_partner.create({
            'name': 'Supplier 1',
            'is_company': True,
            'supplier': True
        })

    def test_onchange_product_tmpl_id(self):

        order = self.purchase_order.create({
            'partner_id': self.supplier.id,

            'order_line': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'price_unit': 100,
                'product_uom': self.product_template_yes.uom_id.id,
                'product_qty': 1,
                'name': 'Line 1',
                'date_planned': '2016-01-01',

            }), (0, 0, {
                'product_tmpl_id': self.product_template_no.id,
                'product_uom': self.product_template_no.uom_id.id,
                'product_qty': 1,
                'price_unit': 200,
                'name': 'Line 2',
                'date_planned': '2016-01-01',
            })]
        })
        line1 = order.order_line[0]
        line2 = order.order_line[1]
        res1 = line1.onchange_product_tmpl_id()
        res2 = line1.onchange_product_tmpl_id_configurator()
        result = dict(res1)
        result.update(res2)
        self.assertEqual(len(line1.product_attribute_ids), 1)
        expected_domain = [
            ('product_tmpl_id', '=', self.product_template_yes.id)
        ]
        self.assertEqual(result['domain']['product_id'], expected_domain)
        line2.onchange_product_tmpl_id()
        line2.onchange_product_tmpl_id_configurator()
        self.assertEqual(line2.product_id,
                         self.product_template_no.product_variant_ids)
        self.assertEqual(line2.name,
                         'Line 2\n%s' %
                         self.product_template_no.description_purchase)

    def test_onchange_product_attribute_ids(self):

        order = self.purchase_order.create({
            'partner_id': self.supplier.id,

            'order_line': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'price_unit': 100,
                'name': 'Line 1',
                'product_qty': 1,
                'date_planned': '2016-01-01',
                'product_uom': self.product_template_yes.uom_id.id,
                'product_attribute_ids': [(0, 0, {
                    'product_tmpl_id': self.product_template_yes.id,
                    'attribute_id': self.attribute1.id,
                    'value_id': self.value1.id,
                    'owner_model': 'purchase.order.line'
                })]
            })]
        })
        line = order.order_line[0]
        with self.cr.savepoint():
            product = self.product_product.create({
                'product_tmpl_id': self.product_template_yes.id,
                'product_attribute_ids': [(0, 0, {
                    'product_tmpl_id': self.product_template_yes.id,
                    'attribute_id': self.attribute1.id,
                    'value_id': self.value1.id
                })]
            })
            line.onchange_product_attribute_ids()
            self.assertEqual(line.product_id, product)

        result = line.onchange_product_attribute_ids()
        expected_domain = [
            ('product_tmpl_id', '=', self.product_template_yes.id),
            ('attribute_value_ids', '=', self.value1.id)
        ]
        self.assertEqual(result['domain'], {'product_id': expected_domain})

    def test_onchange_product_attribute_ids_01(self):
        order = self.purchase_order.create({
            'partner_id': self.supplier.id,

            'order_line': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'price_unit': 100,
                'name': 'Line 1',
                'product_qty': 1,
                'date_planned': '2016-01-01',
                'product_uom': self.product_template_yes.uom_id.id,
                'product_attribute_ids': [(0, 0, {
                    'product_tmpl_id': self.product_template_yes.id,
                    'attribute_id': self.attribute1.id,
                    'value_id': self.value1.id,
                    'owner_model': 'purchase.order.line'
                })]
            })]
        })
        line = order.order_line[0]
        line.onchange_product_attribute_ids()
        self.assertTrue(line.product_id)

    def test_onchange_product_id(self):
        product = self.product_product.create({
            'product_tmpl_id': self.product_template_yes.id,
            'product_attribute_ids': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'attribute_id': self.attribute1.id,
                'value_id': self.value1.id
            })]
        })

        order = self.purchase_order.create({
            'partner_id': self.supplier.id,

            'order_line': [(0, 0, {
                'product_id': product.id,
                'price_unit': 100,
                'name': 'Line 1',
                'product_qty': 1,
                'date_planned': '2016-01-01',
                'product_uom': product.uom_id.id,

            })]
        })

        line = order.order_line[0]
        with self.cr.savepoint():
            line.onchange_product_id()
            line.onchange_product_id_configurator()
            self.assertEqual(len(line.product_attribute_ids), 1)
            self.assertEqual(line.product_tmpl_id, self.product_template_yes)

    def test_button_confirm(self):

        order = self.purchase_order.create({
            'partner_id': self.supplier.id,

            'order_line': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'price_unit': 100,
                'name': 'Line 1',
                'product_qty': 1,
                'date_planned': '2016-01-01',
                'product_uom': self.product_template_yes.uom_id.id,
                'product_attribute_ids': [(0, 0, {
                    'product_tmpl_id': self.product_template_yes.id,
                    'attribute_id': self.attribute1.id,
                    'value_id': self.value1.id,
                    'owner_model': 'purchase.order.line'
                })]
            }), (0, 0, {
                'product_tmpl_id': self.product_template_no.id,
                'product_uom': self.product_template_no.uom_id.id,
                'product_qty': 1,
                'price_unit': 200,
                'name': 'Line 2',
                'date_planned': '2016-01-01',
            })]
        })

        order.button_confirm()

        order_line_without_product = order.order_line.filtered(
            lambda x: not x.product_id)

        self.assertEqual(len(order_line_without_product), 0,
                         "All purchase lines must have a product")
