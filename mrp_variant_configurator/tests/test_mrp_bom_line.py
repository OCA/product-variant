# Copyright 2017 Jose Luis Sandoval Alaguna <jose.alaguna@rotafilo.com.tr>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests.common import SavepointCase


class TestMrpBom(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpBom, cls).setUpClass()

        # ENVIRONMENTS
        cls.product_attribute = cls.env['product.attribute']
        cls.product_attribute_value = cls.env['product.attribute.value']
        cls.product_template = cls.env['product.template'].with_context(
            check_variant_creation=True)
        cls.mrp_bom = cls.env['mrp.bom']
        cls.product_product = cls.env['product.product']
        cls.mrp_bom_line = cls.env['mrp.bom.line']
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

    def test_onchange_product_tmpl_id(self):

        line1 = self.mrp_bom_line.new({
            'product_tmpl_id': self.product_template_yes.id,
            'product_uom': self.product_template_yes.uom_id.id,
            'product_qty': 1,
            'name': 'Line 1',
        })

        result = line1._onchange_product_tmpl_id_configurator()
        self.assertEqual(len(line1.product_attribute_ids), 1)
        expected_domain = [
            ('product_tmpl_id', '=', self.product_template_yes.id)
        ]
        self.assertEqual(result['domain']['product_id'], expected_domain)

        line2 = self.mrp_bom_line.new({
            'product_tmpl_id': self.product_template_no.id,
            'product_uom': self.product_template_no.uom_id.id,
            'product_qty': 1,
            'name': 'Line 2',
        })

        line2._onchange_product_tmpl_id_configurator()
        line2._onchange_product_id_configurator()
        line2.onchange_product_id()
        self.assertEqual(line2.product_id,
                         self.product_template_no.product_variant_ids)
        self.assertEqual(line2.name,
                         '%s\n%s' % (
                             self.product_template_no.name,
                             self.product_template_no.description_purchase
                         ))

    def test_onchange_product_attribute_ids(self):
        product = self.product_product.create({
            'product_tmpl_id': self.product_template_yes.id,
            'product_attribute_ids': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'attribute_id': self.attribute1.id,
                'value_id': self.value1.id
            })]
        })

        line = self.mrp_bom_line.new({
            'product_tmpl_id': self.product_template_yes.id,
            'name': 'Line 1',
            'product_qty': 1,
            'product_uom': self.product_template_yes.uom_id.id,
            'product_attribute_ids': [(0, 0, {
                'product_tmpl_id': self.product_template_yes.id,
                'attribute_id': self.attribute1.id,
                'value_id': self.value1.id,
                'owner_model': 'mrp.bom.line'
            })]
        })

        line._onchange_product_attribute_ids_configurator()
        self.assertEqual(line.product_id, product)

        result = line._onchange_product_attribute_ids_configurator()
        expected_domain = [
            ('product_tmpl_id', '=', self.product_template_yes.id),
            ('attribute_value_ids', '=', self.value1.id)
        ]
        self.assertEqual(result['domain'], {'product_id': expected_domain})

    def test_can_create_product_variant(self):
        line = self.mrp_bom_line.new({
            'product_tmpl_id': self.product_template_yes.id,
            'name': 'Line 1',
            'product_qty': 1,
            'product_uom': self.product_template_yes.uom_id.id,
        })
        self.assertFalse(line.can_create_product)
        attributes = self.env['product.configurator.attribute'].create({
            'product_tmpl_id': self.product_template_yes.id,
            'attribute_id': self.attribute1.id,
            'value_id': self.value1.id,
            'owner_model': 'mrp.bom.line',
            'owner_id': line.id,
        })
        line.product_attribute_ids = attributes
        line._onchange_product_attribute_ids_configurator()
        self.assertTrue(line.can_create_product)
        line.create_product_variant = True
        line._onchange_create_product_variant()
        self.assertTrue(line.product_id)
        self.assertFalse(line.create_product_variant)
