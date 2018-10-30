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
    main_lang = product._guess_main_lang()
    tokens = extract_token(mask)
    attribute_names = set()
    for line in product.attribute_line_ids:
        attribute_names.add(
            line.attribute_id.with_context(lang=main_lang).name)
    if not tokens.issubset(attribute_names):
        raise UserError(_('Found unrecognized attribute name in "Variant '
                          'Reference Mask"'))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    code_prefix = fields.Char(
        string='Reference Prefix', oldname='prefix_code',
        help='Add prefix to product variant reference (default code)',
    )
    reference_mask = fields.Char(
        string='Variant reference mask', copy=False,
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
             ' than once in the mask. Such as,'
             '`fancyA/[Size]~[Color]~[Size]`\n'
             ' When saved, the default code on variants will be '
             'something like \n'
             ' `fancyA/l~r~l` (for variant with Color "Red" and Size "L") '
             ' `fancyA/x~y~x` (for variant with Color "Yellow" and Size "XL")'

             '\nNote: make sure characters "[,]" do not appear in your '
             'attribute name')

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.default_code',
        'code_prefix',
        )
    def _compute_default_code(self):
        super(ProductTemplate, self)._compute_default_code()
        multi_variants = self.filtered(
            lambda template: len(template.product_variant_ids) > 1)
        for template in multi_variants:
            template.default_code = template.code_prefix

    def _get_attr_val_k(self, attr_value_id):
        return attr_value_id.attribute_id.sequence

    def _get_default_mask(self):
        if not self.attribute_line_ids:
            return False
        attribute_names = []
        default_reference_separator = self.env[
            'ir.config_parameter'].get_param('default_reference_separator')
        # impossible to have an empty ir_config_parameter
        if default_reference_separator == 'None':
            default_reference_separator = ''
        for line in sorted(self.attribute_line_ids, key=self._get_attr_val_k):
            attribute_names.append(u"[{}]".format(line.attribute_id.name))
        default_mask = ((self.code_prefix or '') +
                        default_reference_separator.join(attribute_names))
        return default_mask

    def _is_automatic_mask(self):
        return not self.user_has_groups(
            'product_variant_default_code'
            '.group_product_default_code')

    def _synchronyze_default_code(self, vals):
        if 'code_prefix' in vals and \
                not self._context.get('write_product_product') and \
                not self._context.get('create_product_product'):
            vals['default_code'] = vals['code_prefix']
        return vals

    @api.model
    def create(self, vals):
        self._synchronyze_default_code(vals)
        product = self.new(vals)
        if self._is_automatic_mask() or not vals.get('reference_mask'):
            vals['reference_mask'] = product._get_default_mask()
        else:
            sanitize_reference_mask(product, vals['reference_mask'])
        return super(ProductTemplate, self).create(vals)

    def _mask_needs_update(self, vals):
        return 'code_prefix' in vals or 'attribute_line_ids' in vals

    @api.onchange('reference_mask')
    def onchange_reference_mask(self):
        for record in self:
            if not record.reference_mask:
                record.reference_mask = record._get_default_mask()

    def write(self, vals):
        self._synchronyze_default_code(vals)
        result = super(ProductTemplate, self.with_context(
            write_from_tmpl=True)).write(vals)
        if (self._is_automatic_mask() and self._mask_needs_update(vals)):
            for record in self:
                # we write the new mask and the additional write
                # will recompute the variant code
                record.reference_mask = record._get_default_mask()
        if vals.get('reference_mask'):
            cond = [('product_tmpl_id', 'in', self.ids),
                    ('manual_code', '=', False)]
            for product in self.env['product.product'].search(cond):
                product.with_context(
                    write_from_tmpl=True
                ).render_default_code()
        return result

    @api.model
    def _guess_main_lang(self):
        """ Used by get_rendered_default_code()
        """
        english = self.env.ref('base.lang_en')
        if english.active:
            return english.code
        else:
            # Naive/simple implementation:
            # you may inherit to override it in your custom code
            # to return the language code of your choice
            return self.env['res.lang'].search([], limit=1).code


class ProductProduct(models.Model):
    _inherit = 'product.product'

    manual_code = fields.Boolean(string='Manual Reference')

    def _get_rendered_default_code(self):
        product_attrs = defaultdict(str)
        reference_mask = ReferenceMask(self.reference_mask)
        main_lang = self.product_tmpl_id._guess_main_lang()
        for value in self.attribute_value_ids:
            attr_name = value.attribute_id.with_context(lang=main_lang).name
            if value.attribute_id.code:
                product_attrs[attr_name] += value.attribute_id.code
            if value.code:
                product_attrs[attr_name] += value.code
        all_attrs = extract_token(self.reference_mask)
        missing_attrs = all_attrs - set(product_attrs.keys())
        missing = dict.fromkeys(
            missing_attrs,
            self.env['ir.config_parameter'].get_param(
                'default_reference_missing_placeholder'))
        product_attrs.update(missing)
        default_code = reference_mask.safe_substitute(product_attrs)
        return default_code

    def render_default_code(self):
        for record in self:
            record.default_code = record._get_rendered_default_code()

    @api.model
    def create(self, vals):
        if not vals.get('product_tmpl_id') and vals.get('default_code'):
            vals['code_prefix'] = vals['default_code']
        product = super(ProductProduct, self).create(vals)
        if product.reference_mask:
            product.render_default_code()
        return product

    def write(self, vals):
        if 'default_code' in vals and \
                not self._context.get('create_from_tmpl') and \
                not self._context.get('write_from_tmpl'):
            for record in self:
                local_vals = vals.copy()
                if not record.attribute_line_ids:
                    local_vals['code_prefix'] = local_vals['default_code']
                super(ProductProduct, record.with_context(
                    write_product_product=True)).write(local_vals)
            return True
        else:
            return super(ProductProduct, self).write(vals)

    @api.onchange('default_code')
    def onchange_default_code(self):
        for product in self:
            # it shouldn't be possible to be in 'manual_code' mode
            # when there is only 1 variant
            if product.attribute_line_ids:
                self.manual_code = bool(self.default_code)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    code = fields.Char(
        string='Attribute Code',
    )

    _sql_constraints = [
        ('number_uniq', 'unique(name)', _('Attribute Name must be unique!'))]

    def write(self, vals):
        result = super(ProductAttribute, self).write(vals)
        if 'code' not in vals:
            return result
        # Rewrite reference on all product variants affected
        for product in self.mapped('attribute_line_ids').mapped(
            'product_tmpl_id').mapped('product_variant_ids').filtered(
                lambda x: x.product_tmpl_id.reference_mask and not
                x.manual_code):
            product.render_default_code()
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
        result = super(ProductAttributeValue, self).write(vals)
        if 'code' not in vals:
            return result
        # Rewrite reference on all product variants affected
        for product in self.sudo().mapped('product_ids').filtered(
                lambda x: x.product_tmpl_id.reference_mask and not
                x.manual_code
                ).mapped('product_tmpl_id').mapped('product_variant_ids'):
            product.render_default_code()
        return result
