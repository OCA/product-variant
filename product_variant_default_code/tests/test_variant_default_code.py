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
        # Erase the previous mask: 'P01/[TSize][TColor]'
        self.template2.reference_mask = ''
        # Mask is set to default now:
        self.assertEqual(self.template1.reference_mask, '[TSize]-[TColor]')

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
