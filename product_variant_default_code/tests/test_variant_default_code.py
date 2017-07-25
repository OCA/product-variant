# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestVariantDefaultCode(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestVariantDefaultCode, cls).setUpClass()
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
        cls.template = cls.env['product.template'].create({
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

    def test_check_default_codes(self):
        # As no mask was set, a default one should be:
        self.assertEqual(self.template.reference_mask, '[TSize]-[TColor]')
        # Check that variants code are generated according to rules
        for product in self.template.mapped('product_variant_ids'):
            expected_code = (product.attribute_value_ids[0].name[0:2] +
                             '-' + product.attribute_value_ids[1].name[0:2])
            self.assertEqual(product.default_code, expected_code)

    def test_custom_reference_mask(self):
        self.template.reference_mask = u'JKTÜ/[TColor]#[TSize]'
        for product in self.template.mapped('product_variant_ids'):
            expected_code = (u'JKTÜ/' +
                             product.attribute_value_ids[1].name[0:2] + '#' +
                             product.attribute_value_ids[0].name[0:2])
            self.assertEqual(product.default_code, expected_code)
