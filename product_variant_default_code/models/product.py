# -*- coding: utf-8 -*-
# Copyright 2014 AvancOSC - Alfredo de la Fuente
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2014 Shine IT - Tony Gu
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import re
from string import Template
from collections import defaultdict

DEFAULT_REFERENCE_SEPARATOR = '-'
PLACE_HOLDER_4_MISSING_VALUE = '/'


class ReferenceMask(Template):
    pattern = r'''\[(?:
                    (?P<escaped>\[) |
                    (?P<named>[^\]]+?)\] |
                    (?P<braced>[^\]]+?)\] |
                    (?P<invalid>)
                    )'''


def extract_token(s):
    pattern = re.compile(r'\[([^\]]+?)\]')
    return set(pattern.findall(s))


def sanitize_reference_mask(product, mask):
    tokens = extract_token(mask)
    attribute_names = set()
    for line in product.attribute_line_ids:
        attribute_names.add(line.attribute_id.name)
    if not tokens.issubset(attribute_names):
        raise UserError(_('Found unrecognized attribute name in "Variant '
                          'Reference Mask"'))


def get_rendered_default_code(product, mask):
    product_attrs = defaultdict(str)
    reference_mask = ReferenceMask(mask)
    for value in product.attribute_value_ids:
        if value.attribute_id.code:
            product_attrs[value.attribute_id.name] += value.attribute_id.code
        if value.code:
            product_attrs[value.attribute_id.name] += value.code
    all_attrs = extract_token(mask)
    missing_attrs = all_attrs - set(product_attrs.keys())
    missing = dict.fromkeys(missing_attrs, PLACE_HOLDER_4_MISSING_VALUE)
    product_attrs.update(missing)
    default_code = reference_mask.safe_substitute(product_attrs)
    return default_code


def render_default_code(product, mask):
    product.default_code = get_rendered_default_code(product, mask)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    reference_mask = fields.Char(
        string='Variant reference mask',
        help='Reference mask for building internal references of a '
             'variant generated from this template.\n'

             'Example:\n'
             'A product named ABC with 2 attributes: Size and Color:\n'

             'Product: ABC\n'
             'Color: Red(r), Yellow(y), Black(b)  #Red, Yellow, Black are '
             'the attribute value, `r`, `y`, `b` are the corresponding code\n'
             'Size: L (l), XL(x)\n'

             'When setting Variant reference mask to `[Color]-[Size]`, the '
             'default code on the variants will be something like `r-l` '
             '`b-l` `r-x` ...\n'

             'If you like, You can even have the attribute name appear more'
             ' than once in the mask. Such as , `fancyA/[Size]~[Color]~[Size]`'
             ' When saved, the default code on variants will be something like'
             ' `fancyA/l~r~l` (for variant with Color "Red" and Size "L") '
             '`fancyA/x~y~x` (for variant with Color "Yellow" and Size "XL")\n'

             'Note: make sure characters "[,]" do not appear in your '
             'attribute name')

    @api.model
    def create(self, vals):
        product = self.new(vals)
        if not vals.get('reference_mask') and product.attribute_line_ids:
            attribute_names = []
            for line in product.attribute_line_ids:
                attribute_names.append("[{}]".format(line.attribute_id.name))
            default_mask = DEFAULT_REFERENCE_SEPARATOR.join(attribute_names)
            vals['reference_mask'] = default_mask
        elif vals.get('reference_mask'):
            sanitize_reference_mask(product, vals['reference_mask'])
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        product_obj = self.env['product.product']
        if 'reference_mask' in vals and not vals['reference_mask']:
            if self.attribute_line_ids:
                attribute_names = []
                for line in self.attribute_line_ids:
                    attribute_names.append("[{}]".format(
                        line.attribute_id.name))
                default_mask = DEFAULT_REFERENCE_SEPARATOR.join(
                    attribute_names)
                vals['reference_mask'] = default_mask
        result = super(ProductTemplate, self).write(vals)
        if vals.get('reference_mask'):
            cond = [('product_tmpl_id', '=', self.id),
                    ('manual_code', '=', False)]
            products = product_obj.search(cond)
            for product in products:
                if product.reference_mask:
                    render_default_code(product, product.reference_mask)
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    manual_code = fields.Boolean(string='Manual code')

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        if product.reference_mask:
            render_default_code(product, product.reference_mask)
        return product

    @api.onchange('default_code')
    def onchange_default_code(self):
        self.manual_code = bool(self.default_code)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    code = fields.Char(
        string='Attribute Code',
    )

    _sql_constraints = [
        ('number_uniq', 'unique(name)', _('Attribute Name must be unique!'))]

    def write(self, vals):
        if 'code' not in vals:
            return super(ProductAttribute, self).write(vals)
        result = super(ProductAttribute, self).write(vals)
        # Rewrite reference on all product variants affected
        for product in self.mapped('attribute_line_ids').mapped(
            'product_tmpl_id').mapped('product_variant_ids').filtered(
                lambda x: x.product_tmpl_id.reference_mask and not
                x.manual_code):
            render_default_code(product, product.reference_mask)
        return result


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.code = self.name[0:2]

    code = fields.Char(
        string='Attribute Value Code',
        default=onchange_name,
        oldname='attribute_code',
    )

    @api.model
    def create(self, vals):
        if 'code' not in vals:
            vals['code'] = vals.get('name', '')[0:2]
        return super(ProductAttributeValue, self).create(vals)

    def write(self, vals):
        if 'code' not in vals:
            return super(ProductAttributeValue, self).write(vals)
        result = super(ProductAttributeValue, self).write(vals)
        # Rewrite reference on all product variants affected
        for product in self.mapped('product_ids').filtered(
                lambda x: x.product_tmpl_id.reference_mask and not
                x.manual_code):
            render_default_code(product, product.reference_mask)
        return result
