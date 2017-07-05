# -*- coding: utf-8 -*-
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import SavepointCase


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
            'supplier': True,
        })

    def test_onchange_product_tmpl_id(self):
        order = self.purchase_order.create({
            'partner_id': self.supplier.id,

        })
        line1 = self.purchase_order_line.new({
            'order_id': order.id,
            'product_tmpl_id': self.product_template_yes.id,
            'price_unit': 100,
            'product_uom': self.product_template_yes.uom_id.id,
            'product_qty': 1,
            'name': 'Line 1',
            'date_planned': '2017-01-01',

        })
        line1.product_tmpl_id = self.product_template_no
        line1.onchange_product_tmpl_id()
        self.assertEqual(line1.name, self.product_template_no.name)
