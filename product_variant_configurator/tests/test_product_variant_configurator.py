# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SavepointCase
from openerp.exceptions import ValidationError


class TestProductVariantConfigurator(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductVariantConfigurator, cls).setUpClass()

        # ENVIRONMENTS
        cls.product_attribute = cls.env['product.attribute']
        cls.product_attribute_value = cls.env['product.attribute.value']
        cls.product_category = cls.env['product.category']
        cls.product_product = cls.env['product.product']
        cls.product_template = cls.env['product.template'].with_context(
            check_variant_creation=True)

        # INSTANCES
        # Instances: product category
        cls.category1 = cls.product_category.create({
            'name': 'No create variants category',
        })
        cls.category2 = cls.product_category.create({
            'name': 'Create variants category',
            'no_create_variants': False,
        })
        # Instances: product attribute
        cls.attribute1 = cls.product_attribute.create({
            'name': 'Test Attribute 1',
        })
        cls.attribute2 = cls.product_attribute.create({
            'name': 'Test Attribute 2',
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
        cls.value3 = cls.product_attribute_value.create({
            'name': 'Value 3',
            'attribute_id': cls.attribute2.id,
        })
        cls.value4 = cls.product_attribute_value.create({
            'name': 'Value 4',
            'attribute_id': cls.attribute2.id,
        })
        # Instances: product template
        cls.product_template_yes = cls.product_template.create({
            'name': 'Product template 1',
            'no_create_variants': 'yes',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attribute1.id,
                        'value_ids': [(6, 0, [cls.value1.id,
                                              cls.value2.id])]})],
        })
        cls.product_template_no = cls.product_template.create({
            'name': 'Product template 2',
            'no_create_variants': 'no',
        })
        cls.product_template_empty_no = cls.product_template.create({
            'name': 'Product template 3',
            'no_create_variants': 'empty',
            'categ_id': cls.category1.id,
        })
        cls.product_template_empty_yes = cls.product_template.create({
            'name': 'Product template 3',
            'no_create_variants': 'empty',
            'categ_id': cls.category2.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attribute1.id,
                        'value_ids': [(6, 0, [cls.value1.id,
                                              cls.value2.id])]})],
        })

    def test_no_create_variants(self):
        tmpl = self.product_template.create({
            'name': 'No create variants template',
            'no_create_variants': 'yes',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute1.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertEquals(len(tmpl.product_variant_ids), 0)
        tmpl = self.product_template.create({
            'name': 'No variants template',
            'no_create_variants': 'yes',
        })
        self.assertEquals(len(tmpl.product_variant_ids), 0)

    def test_no_create_variants_category(self):
        self.assertTrue(self.category1.no_create_variants)
        tmpl = self.product_template.create({
            'name': 'Category option template',
            'categ_id': self.category1.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute1.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEquals(len(tmpl.product_variant_ids), 0)
        tmpl = self.product_template.create({
            'name': 'No variants template',
            'categ_id': self.category1.id,
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEquals(len(tmpl.product_variant_ids), 0)

    def test_create_variants(self):
        tmpl = self.product_template.create({
            'name': 'Create variants template',
            'no_create_variants': 'no',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute1.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertEquals(len(tmpl.product_variant_ids), 2)
        tmpl = self.product_template.create({
            'name': 'No variants template',
            'no_create_variants': 'no',
        })
        self.assertEquals(len(tmpl.product_variant_ids), 1)

    def test_create_variants_category(self):
        self.assertFalse(self.category2.no_create_variants)
        tmpl = self.product_template.create({
            'name': 'Category option template',
            'categ_id': self.category2.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute1.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEquals(len(tmpl.product_variant_ids), 2)
        tmpl = self.product_template.create({
            'name': 'No variants template',
            'categ_id': self.category2.id,
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEquals(len(tmpl.product_variant_ids), 1)

    def test_category_change(self):
        self.assertTrue(self.category1.no_create_variants)
        tmpl = self.product_template.create({
            'name': 'Category option template',
            'categ_id': self.category1.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute1.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEquals(len(tmpl.product_variant_ids), 0)
        self.category1.no_create_variants = False
        self.assertEquals(len(tmpl.product_variant_ids), 2)

    def test_get_product_attributes_dict(self):
        attrs_dict = self.product_template_yes._get_product_attributes_dict()
        self.assertEquals(len(attrs_dict), 1)
        self.assertEquals(len(attrs_dict[0]), 1)

    def test_get_product_description(self):
        product = self.product_product.create({
            'name': 'Test product',
            'product_tmpl_id': self.product_template_yes.id
        })
        self.assertEquals(product._get_product_description(
            product.product_tmpl_id, product, product.attribute_value_ids),
            'Test product')

        self.current_user = self.env.user
        # Add current user to group: group_supplier_inv_check_total
        group_id = (
            'product_variant_configurator.'
            'group_product_variant_extended_description')
        self.env.ref(group_id).write({'users': [(4, self.current_user.id)]})

        self.assertEquals(product._get_product_description(
            product.product_tmpl_id, product, product.attribute_value_ids),
            'Test product')

    def test_onchange_product_tmpl_id(self):
        product = self.product_product.create({
            'name': 'Test product',
            'product_tmpl_id': self.product_template_yes.id
        })
        with self.cr.savepoint(), self.assertRaises(ValidationError):
            product.product_tmpl_id = self.product_template_no
            product.onchange_product_tmpl_id()

        product.product_tmpl_id = self.product_template_empty_no
        res = product.onchange_product_tmpl_id()
        self.assertEquals(
            res, {'domain': {'product_id': [
                ('product_tmpl_id', '=', self.product_template_empty_no.id)]}})

    def test_templ_name_search(self):
        res = self.product_template.name_search('Product template 222')
        for r in res:
            if r[0] == self.product_template_no.id:
                self.fail()
        res = self.product_template.name_search('Product template 2')
        for r in res:
            if r[0] == self.product_template_no.id:
                return
        self.fail()
