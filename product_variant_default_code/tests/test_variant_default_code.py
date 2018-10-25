# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests import common


class TestVariantDefaultCode(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestVariantDefaultCode, cls).setUpClass()
        cls.group_default_code = cls.env.ref(
            'product_variant_default_code.group_product_default_code')
        cls.attr1 = cls.env['product.attribute'].create({'name': 'TSize'})
        cls.attr2 = cls.env['product.attribute'].create({'name': 'TColor'})
        cls.attr1_1 = cls.env['product.attribute.value'].create({
            'name': 'L', 'attribute_id': cls.attr1.id
        })
        cls.attr1_2 = cls.env['product.attribute.value'].create({
            'name': 'XL', 'attribute_id': cls.attr1.id
        })
        cls.attr2_1 = cls.env['product.attribute.value'].create({
            'name': 'Red', 'attribute_id': cls.attr2.id
        })
        cls.attr2_2 = cls.env['product.attribute.value'].create({
            'name': 'Green', 'attribute_id': cls.attr2.id
        })
        cls.template1 = cls.env['product.template'].create({
            'name': 'Jacket',
            'attribute_line_ids':  [
                (0, 0, {'attribute_id': cls.attr1.id,
                        'value_ids': [(6, 0, [cls.attr1_1.id, cls.attr1_2.id])]
                        }),
                (0, 0, {'attribute_id': cls.attr2.id,
                        'value_ids': [(6, 0, [cls.attr2_1.id, cls.attr2_2.id])]
                        }),
            ],
        })
        # This one with a preset reference mask
        cls.template2 = cls.env['product.template'].create({
            'name': 'Pants',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attr1.id,
                        'value_ids': [(6, 0, [cls.attr1_1.id, cls.attr1_2.id])]
                        }),
                (0, 0, {'attribute_id': cls.attr2.id,
                        'value_ids': [(6, 0, [cls.attr2_1.id, cls.attr2_2.id])]
                        }),
            ],
            'reference_mask': 'P01/[TSize][TColor]',
        })
        # Only one attribute
        cls.template3 = cls.env['product.template'].create({
            'name': 'Socks',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attr1.id,
                        'value_ids': [(6, 0, [cls.attr1_1.id, cls.attr1_2.id])]
                        })
            ]
        })

    def test_01_check_default_codes(self):
        # As no mask was set, a default one should be:
        self.assertEqual(self.template1.reference_mask, '[TSize]-[TColor]')
        # Check that variants code are generated according to rules
        for product in self.template1.mapped('product_variant_ids'):
            expected_code = (
                product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr1).name[0:2] + '-' +
                product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr2).name[0:2])
            self.assertEqual(product.default_code, expected_code)

    def test_02_check_default_codes_preexistent_mask(self):
        self.env.user.groups_id |= self.group_default_code
        self.template2.reference_mask = 'P01/[TSize][TColor]'
        for product in self.template2.mapped('product_variant_ids'):
            expected_code = (
                'P01/' + product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr1).name[0:2] +
                product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr2).name[0:2])
            self.assertEqual(product.default_code, expected_code)

    def test_03_reset_reference_mask_to_default(self):
        self.env.user.groups_id |= self.group_default_code
        # Erase the previous mask: 'P01/[TSize][TColor]'
        self.template2.write({'reference_mask': ''})
        self.template2.onchange_reference_mask()
        # Mask is set to default now:
        self.assertEqual(self.template2.reference_mask, '[TSize]-[TColor]')

    def test_04_custom_reference_mask(self):
        self.env.user.groups_id |= self.group_default_code
        self.template1.reference_mask = u'JKTÜ/[TColor]#[TSize]'
        for product in self.template1.mapped('product_variant_ids'):
            expected_code = (
                u'JKTÜ/' + product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr2).name[0:2] + '#' +
                product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr1).name[0:2])
            self.assertEqual(product.default_code, expected_code)

    def test_05_manual_code(self):
        self.env.user.groups_id |= self.group_default_code
        self.assertEqual(self.template1.product_variant_ids[0].manual_code,
                         False)
        self.template1.product_variant_ids[0].default_code = 'CANT-TOUCH-THIS'
        self.template1.product_variant_ids[0].onchange_default_code()
        self.assertEqual(self.template1.product_variant_ids[0].manual_code,
                         True)
        # Set a reference mask and check the other variants are changed
        self.template1.reference_mask = 'J[TColor][TSize]'
        for product in self.template1.mapped('product_variant_ids')[1:]:
            expected_code = (
                'J' + product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr2).name[0:2] +
                product.attribute_value_ids.filtered(
                    lambda x: x.attribute_id == self.attr1).name[0:2])
            self.assertEqual(product.default_code, expected_code)
        # But this one isn't:
        self.assertEqual(self.template1.product_variant_ids[0].default_code,
                         'CANT-TOUCH-THIS')

    def test_06_attribute_value_code_change_propagation(self):
        self.attr1_1.code = 'OO'
        # Check that the change spreads to every product
        for product in self.attr1_1.mapped('product_ids'):
            self.assertTrue('OO' in product.default_code)

    def test_07_attribute_value_name_change(self):
        self.attr1_1.name = 'Odoo'
        self.attr1_1.onchange_name()
        self.assertEqual(self.attr1_1.code, 'Od')
        # Check that the change spreads to every product
        for product in self.attr1_1.mapped('product_ids'):
            self.assertTrue('Od' in product.default_code)

    def test_08_sanitize_exception(self):
        self.env.user.groups_id |= self.group_default_code
        with self.assertRaises(UserError):
            self.env['product.template'].create({
                'name': 'Shirt',
                'attribute_line_ids': [
                    (0, 0, {'attribute_id': self.attr1.id,
                            'value_ids': [(6, 0, [self.attr1_1.id])]
                            }),
                ],
                'reference_mask': 'FAIL:[TSize][TWrongAttr]',
            })

    def test_09_code_change_propagation(self):
        self.attr1.code = 'AC'
        # Check that the change spreads to every product
        for product in self.attr1.mapped('attribute_line_ids').mapped(
                'product_tmpl_id').mapped('product_variant_ids'):
            self.assertTrue('AC' in product.default_code)

    def test_10_code_change_propagation_archived_variant(self):
        self.template1.product_variant_ids[0].active = False
        self.attr1.code = 'o_o'
        self.assertTrue(
            'o_o' in self.template1.product_variant_ids[0].default_code)
        self.attr1_1.code = '^_^'
        self.assertTrue(
            '^_^' in self.template1.product_variant_ids[0].default_code)

    def test_11_check_none_separator(self):
        self.env.user.groups_id |= self.group_default_code
        self.env['ir.config_parameter'].set_param(
            'default_reference_separator', 'None')
        # re-initialize reference mask
        self.template2.write({'reference_mask': ''})
        self.template2.onchange_reference_mask()
        self.assertEqual(self.template2.reference_mask, '[TSize][TColor]')

    def test_12_check_code_prefix_modification(self):
        # Automatic mode
        self.template1.write({'code_prefix': 'AA'})
        self.assertEqual(self.template1.reference_mask, 'AA[TSize]-[TColor]')

    def test_13_write_on_multiple_record(self):
        templates = self.template1 | self.template2
        templates.write({'list_price': 4})
        for template in templates:
            self.assertEqual(template.list_price, 4)

    def test_14_check_attribute_lines_modification(self):
        self.assertEqual(self.template3.reference_mask, '[TSize]')
        self.template3.write({
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attr2.id,
                        'value_ids': [
                            (6, 0, [self.attr2_1.id, self.attr2_2.id])]
                        }),
            ]
        })
        self.assertEqual(self.template3.reference_mask, '[TSize]-[TColor]')

    def test_15_check_create_edit_variant(self):
        variant = self.env['product.product'].create({
            'name': 'create_variant',
            'default_code': '123456'
        })
        self.assertEqual(variant.product_tmpl_id.code_prefix, '123456')
        variant.write({
            'default_code': '99999'
        })
        self.assertEqual(variant.product_tmpl_id.code_prefix, '99999')

    def test_16_check_create_edit_template(self):
        template = self.env['product.template'].create({
            'name': 'create_template',
            'code_prefix': '654321'
        })
        self.assertEqual(template.product_variant_ids.default_code, '654321')
        template.write({
            'code_prefix': '111111'
        })
        self.assertEqual(template.product_variant_ids.default_code, '111111')
