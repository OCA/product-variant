# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
import collections
import re
from string import Template
from collections import defaultdict

from openerp import models, fields, api, tools, SUPERUSER_ID, exceptions, _
from openerp.addons import decimal_precision as dp
from openerp.osv import osv


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
        raise except_orm(_('Error'), _('Found unrecognized attribute name in '
                                       '"Variant Reference Mask"'))


def render_default_code(attribute_value_ids, mask):
    product_attrs = defaultdict(str)
    reference_mask = ReferenceMask(mask)
    for value in attribute_value_ids:
        if value.attribute_code:
            product_attrs[value.attribute_id.name] += value.attribute_code
    all_attrs = extract_token(mask)
    missing_attrs = all_attrs - set(product_attrs.keys())
    missing = dict.fromkeys(missing_attrs, PLACE_HOLDER_4_MISSING_VALUE)
    product_attrs.update(missing)
    default_code = reference_mask.safe_substitute(product_attrs)
    return default_code


class ProductAttributeValueSaleLine(models.Model):
    _name = 'product.product.attribute'

    @api.one
    @api.depends('value', 'product_product.product_template')
    def _get_price_extra(self):
        price_extra = 0.0
        for price in self.value.price_ids:
            if price.product_tmpl_id.id == self.product_product.product_template.id:
                price_extra = price.price_extra
        self.price_extra = price_extra

    @api.one
    @api.depends('attribute', 'product_product.product_template',
                 'product_product.product_template.attribute_line_ids')
    def _get_possible_attribute_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.product_product.product_template.attribute_line_ids:
            if attr_line.attribute_id.id == self.attribute.id:
                attr_values |= attr_line.value_ids
        self.possible_values = attr_values.sorted()

    product_product = fields.Many2one(
        comodel_name='product.product', string='Product1')
    attribute = fields.Many2one(
        comodel_name='product.attribute', string='Attribute')
    value = fields.Many2one(
        comodel_name='product.attribute.value', string='Value',
        domain="[('id', 'in', possible_values[0][2])]")
    possible_values = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_get_possible_attribute_values')
    price_extra = fields.Float(
        compute='_get_price_extra', string='Attribute Price Extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with this attribute"
        " value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")


class ProductVariants(models.Model):
    _inherit = 'product.product'

    #order_state = fields.Selection(related='order_id.state', readonly=True)
    product_template = fields.Many2one(comodel_name='product.template',
                                       string='Product Template')
    product_attributes = fields.One2many(
        comodel_name='product.product.attribute', inverse_name='product_product',
        string='Product attributes', copy=True)
    product_copy = fields.Many2one('product.product')

    @api.multi
    @api.onchange('product_template')
    def onchange_product_template2(self):
        
        self.ensure_one()
        self.name = self.product_template.name
        if not self.product_template.attribute_line_ids:
            self.product_id = (
                self.product_template.product_variant_ids and
                self.product_template.product_variant_ids[0])
        #else:
            #self.product_id = False
            # TODO
            # check this
            '''
            self.price_unit = self.order_id.pricelist_id.with_context(
                {
                    'uom': self.product_uom.id,
                    'date': self.order_id.date_order,
                }).template_price_get(
                self.product_template.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
            '''
        self.product_attributes = (
            self.product_template._get_product_attributes_dict())
        return {'domain': {'product_id': [('product_tmpl_id', '=',
                                           self.product_template.id)]}}

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context={}
        
        context.update({'product_copy': id})
        return super(ProductVariants, self).copy(cr, uid, id, default=default, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context={}

        if vals.get('product_attributes'):
            newly_changed = [at[2]['value'] for at in vals.get('product_attributes') if at[2]]
            changed = self.pool.get('product.attribute.value').browse(cr, uid, newly_changed)
            this = self.browse(cr, uid, ids)
            original = self.pool.get('product.product').browse(cr, uid, this.product_copy.id)
            org_attrs = {}
            for at in original.attribute_value_ids:
                org_attrs.update({at.attribute_id.id: at.id})

            ch_attrs = {}
            for at in changed:

                ch_attrs.update({at.attribute_id.id: at.id})

            for key in ch_attrs.keys():
                org_attrs[key] = ch_attrs[key]

            org = collections.OrderedDict(sorted(org_attrs.items()))
            
            new_attribute_ids = [v for k, v in org.iteritems()]
            
            attribute_objects = self.pool.get('product.attribute.value').\
                browse(cr, uid, new_attribute_ids, context=context)

            mask = this.reference_mask
            default_code = render_default_code(attribute_objects, mask)
            vals.update({'attribute_value_ids': [(6, 0, new_attribute_ids)],
                'default_code': default_code})
        result = super(ProductVariants, self).write(cr, uid, ids, vals, context=context)
        return result
          
    def create(self, cr, uid, vals, context=None):
        product_obj = self.pool.get('product.product')
        if context.get('do_not_recreate'):
            return super(ProductVariants, self).create(cr, uid, vals, context=context)
        
        if vals.get('product_attributes') and not context.get('product_copy') and not context.get('do_not_recreate', False):    
            context.update({'do_not_recreate': True})
            attributes = dict()
            for at in vals.get('product_attributes'):
                try:
                    attributes.update({at[2]['attribute']: at[2]['value']})
                except BaseException as e:
                    raise exceptions.Warning(
                        _("You can not confirm before configuring all"
                          " attribute values."))
            
            ordered_attrs = collections.OrderedDict(sorted(attributes.items()))

            att_values_ids = [v for k, v in ordered_attrs.iteritems()]
            domain = [('product_tmpl_id', '=', vals.get('product_template'))]
            for value in att_values_ids:
                if not value:
                    raise exceptions.Warning(
                        _("You can not confirm before configuring all"
                          " attribute values."))
                domain.append(('attribute_value_ids', '=', value))
            product = product_obj.search(cr, uid, domain, context=context)

            if not product:
                
                product_id = product_obj.create(cr, uid, vals=
                {'product_tmpl_id': vals.get('product_template'),
                'product_template': vals.get('product_template'),
                 'attribute_value_ids': [(6, 0, att_values_ids)],
                 'product_attributes': vals.get('product_attributes')}, context=context) 
                return product_id
            else:
                raise exceptions.Warning(
                        _("You are trying to create product with same attributes"))

        elif context.get('product_copy'):
            context.update({'do_not_recreate': True})
            
            product_id = product_obj.create(cr, uid, vals=
            {'product_tmpl_id': vals.get('product_template'),
            'product_template': vals.get('product_template'),
            'product_attributes': vals.get('product_attributes'),
            'product_copy': context.get('product_copy')
            }, context=context) 
            
            return product_id
        else:
            return super(ProductVariants, self).create(cr, uid, vals, context=context)

    @api.multi
    def update_price_unit(self):
        self.ensure_one()
        if not self.product_id:
            price_extra = 0.0
            for attr_line in self.product_attributes:
                price_extra += attr_line.price_extra
            '''
            self.price_unit = self.order_id.pricelist_id.with_context(
                {
                    'uom': self.product_uom.id,
                    'date': self.order_id.date_order,
                    'price_extra': price_extra,
                }).template_price_get(
                self.product_template.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
            '''

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name','')
            code = context.get('display_default_code', True) and d.get('default_code',False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):

            
            name = product.product_tmpl_id.name
            attributes = dict()
            

            for attr_line in product.attribute_value_ids:
                attributes.update({attr_line.attribute_id.id: {'attr_name': attr_line.attribute_id.name,
                    'attr_value_name': attr_line.name}})                
                
            ordered_attrs = collections.OrderedDict(sorted(attributes.items()))
            for k, v in ordered_attrs.iteritems():
                name += _(' ; %s: %s') % (v['attr_name'], v['attr_value_name'])

            sellers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and (
                        variant and "%s (%s)" % (s.product_name, variant) or s.product_name
                        ) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))

        return result

class ManualVariantAttributes(osv.osv):
    _inherit = "product.attribute.value"
    
    def name_get(self, cr, uid, ids, context=None):
        if context and not context.get('show_attribute', True):
            return super(ManualVariantAttributes, self).name_get(cr, uid, ids, context=context)
        res = []

        
        objects = [obj for obj in self.browse(cr, uid, ids, context=context)]

        # if listing attribute values for same attribute type
        if len(objects) > 1 and objects[0].attribute_id.id == objects[1].attribute_id.id:
            for value in objects:
                res.append([value.id, "%s: %s" % (value.attribute_id.name, value.name)])
            return res

        attributes = dict()
        # if showing attributes vales for same product.product
        for attr_line in objects:
            attributes.update({attr_line.attribute_id.id: {'attr_name': attr_line.attribute_id.name,
                    'attr_value_name': attr_line.name, 'id': attr_line.id}}) 

        ordered_attrs = collections.OrderedDict(sorted(attributes.items()))

        for k, v in ordered_attrs.iteritems():
            res.append([v['id'], "%s: %s" % (v['attr_name'], v['attr_value_name'])])
        return res


class ManualVariantSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    
    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
            name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        product_obj = self.env['product.product']
        res = super(ManualVariantSaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        
        if (product_obj.browse(product).attribute_value_ids and name and
                'value' in res and 'name' in res['value'] and
                name != res['value']['name']):
            
            this = product_obj.browse(product)
            description = this.product_tmpl_id.name
            attributes = dict()
            if not this.attribute_value_ids:
                return res
            for attr_line in this.attribute_value_ids:
                attributes.update({attr_line.attribute_id.id: {'attr_name': attr_line.attribute_id.name,
                    'attr_value_name': attr_line.name}})                
                
            ordered_attrs = collections.OrderedDict(sorted(attributes.items()))
            for k, v in ordered_attrs.iteritems():
                description += _(' ; %s: %s') % (v['attr_name'], v['attr_value_name'])
            res['value'].update({'name': description})

        return res
