# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import decimal_precision as dp
import netsvc
# Lib to eval python code with security
from tools.safe_eval import safe_eval

#
# Dimensions Definition
#
class product_variant_dimension_type(osv.osv):
    _name = "product.variant.dimension.type"
    _description = "Dimension Type"

    _columns = {
        'description': fields.char('Description', size=64, translate=True),
        'name' : fields.char('Dimension', size=64, required=True),
        'sequence' : fields.integer('Sequence', help="The product 'variants' code will use this to order the dimension values"),
        'value_ids' : fields.one2many('product.variant.dimension.value', 'dimension_id', 'Dimension Values'),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', ondelete='cascade'),
        'allow_custom_value': fields.boolean('Allow Custom Value', help="If true, custom values can be entered in the product configurator"),
        'mandatory_dimension': fields.boolean('Mandatory Dimension', help="If false, variant products will be created with and without this dimension"),
    }

    _defaults = {
        'mandatory_dimension': lambda *a: 1,
        }
    
    _order = "sequence, name"

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=None):
        if context.get('product_tmpl_id', False):
            return super(product_variant_dimension_type, self).name_search(cr, user, '', args, 'ilike', None, None)
        else:
            return super(product_variant_dimension_type, self).name_search(cr, user, '', None, 'ilike', None, None)

product_variant_dimension_type()


class product_variant_dimension_value(osv.osv):
    _name = "product.variant.dimension.value"
    _description = "Dimension Value"

    def _get_dimension_values(self, cr, uid, ids, context={}):
        return self.pool.get('product.variant.dimension.value').search(cr, uid, [('dimension_id', 'in', ids)], context=context)

    _columns = {
        'name' : fields.char('Dimension Value', size=64, required=True),
        'sequence' : fields.integer('Sequence'),
        'price_extra' : fields.float('Sale Price Extra', digits_compute=dp.get_precision('Sale Price')),
        'price_margin' : fields.float('Sale Price Margin', digits_compute=dp.get_precision('Sale Price')),
        'cost_price_extra' : fields.float('Cost Price Extra', digits_compute=dp.get_precision('Purchase Price')),
        'dimension_id' : fields.many2one('product.variant.dimension.type', 'Dimension Type', ondelete='cascade'),
        'product_tmpl_id': fields.related('dimension_id', 'product_tmpl_id', type="many2one", relation="product.template", string="Product Template", store=True),
        'dimension_sequence': fields.related('dimension_id', 'sequence', string="Related Dimension Sequence",#used for ordering purposes in the "variants"
             store={
                'product.variant.dimension.type': (_get_dimension_values, ['sequence'], 10),
            }),
    }
    _order = "dimension_sequence, sequence, name"

product_variant_dimension_value()


class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'dimension_type_ids':fields.one2many('product.variant.dimension.type', 'product_tmpl_id', 'Dimension Types'),
        'variant_ids':fields.one2many('product.product', 'product_tmpl_id', 'Variants'),
        'variant_model_name':fields.char('Variant Model Name', size=64, required=True, help='[NAME] will be replaced by the name of the dimension and [VALUE] by is value. Example of Variant Model Name : "[NAME] - [VALUE]"'),
        'variant_model_name_separator':fields.char('Variant Model Name Separator', size=64, help= 'Add a separator between the elements of the variant name'),
        'code_generator' : fields.char('Code Generator', size=64, help='enter the model for the product code, all parameter between [_o.my_field_] will be replace by the product field. Example product_code model : prefix_[_o.variants_]_suffixe ==> result : prefix_2S2T_suffix'),
        'is_multi_variants' : fields.boolean('Is Multi Variants?'),
    }
    
    _defaults = {
        'variant_model_name': lambda *a: '[NAME] - [VALUE]',
        'variant_model_name_separator': lambda *a: ' - ',
        'is_multi_variants' : lambda *a: False,
                }
    def get_products_from_product_template(self, cr, uid, ids, context={}):
        product_tmpl = self.read(cr, uid, ids, ['variant_ids'], context=context)
        return [id for vals in product_tmpl for id in vals['variant_ids']]
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'variant_ids':False,})
        return super(product_template, self).copy(cr, uid, id, default, context)

    def copy_translations(self, cr, uid, old_id, new_id, context=None):
        if context is None:
            context = {}
        # avoid recursion through already copied records in case of circular relationship
        seen_map = context.setdefault('__copy_translations_seen',{})
        if old_id in seen_map.setdefault(self._name,[]):
            return
        seen_map[self._name].append(old_id)
        return super(product_template, self).copy_translations(cr, uid, old_id, new_id, context=context)

    def _create_variant_list(self, cr, ids, uid, vals, context=None):
        
        def cartesian_product(args):
            if len(args) == 1: return [x and [x] or [] for x in args[0]]
            return [(i and [i] or []) + j for j in cartesian_product(args[1:]) for i in args[0]]
        
        return cartesian_product(vals)

    def button_generate_variants(self, cr, uid, ids, context={}):
        logger = netsvc.Logger()
        variants_obj = self.pool.get('product.product')
        temp_val_list=[]

        for product_temp in self.browse(cr, uid, ids, context):
            for temp_type in product_temp.dimension_type_ids:
                temp_val_list.append([temp_type_value.id for temp_type_value in temp_type.value_ids] + (not temp_type.mandatory_dimension and [None] or []))
                # if last dimension_type has no dimension_value, we ignore it
                if not temp_val_list[-1]:
                    temp_val_list.pop()

            if temp_val_list:
                list_of_variants = self._create_variant_list(cr, uid, ids, temp_val_list, context)
                existing_product_ids = variants_obj.search(cr, uid, [('product_tmpl_id', '=', product_temp.id)])
                existing_product_dim_value = variants_obj.read(cr, uid, existing_product_ids, ['dimension_value_ids'])
                list_of_variants_existing = [x['dimension_value_ids'] for x in existing_product_dim_value]
                for x in list_of_variants_existing:
                    x.sort()
                for x in list_of_variants:
                    x.sort()                  
                list_of_variants_to_create = [x for x in list_of_variants if not x in list_of_variants_existing]
                
                logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "variant existing : %s, variant to create : %s" % (len(list_of_variants_existing), len(list_of_variants_to_create)))
                count = 0
                for variant in list_of_variants_to_create:
                    count += 1
                    
                    vals={}
                    vals['product_tmpl_id']=product_temp.id
                    vals['dimension_value_ids']=[(6,0,variant)]
    
                    var_id=variants_obj.create(cr, uid, vals, {})
                                        
                    if count%50 == 0:
                        cr.commit()
                        logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "product created : %s" % (count,))
                logger.notifyChannel('product_variant_multi', netsvc.LOG_INFO, "product created : %s" % (count,))
        return True


    def button_generate_product_code(self, cr, uid, ids, context={}):
        product_ids = self.get_products_from_product_template(cr, uid, ids, context=context)
        self.pool.get('product.product').build_product_code(cr, uid, product_ids, context=context)
        return True
        
product_template()


class product_product(osv.osv):
    _inherit = "product.product"

    def parse(self, cr, uid, o, text, context=None):
        if not text:
            return ''
        vals = text.split('[_')
        description = ''
        for val in vals:
            if '_]' in val:
                sub_val = val.split('_]')
                description += (safe_eval(sub_val[0], {'o' :o, 'context':context}) or '' ) + sub_val[1]
            else:
                description += val
        return description

    def build_product_code(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            default_code = self.parse(cr, uid, product, product.product_tmpl_id.code_generator, context=context)
            self.write(cr, uid, product.id, {'default_code':default_code}, context=context)
        return True

    def product_ids_variant_changed(self, cr, uid, ids, res, context=None):
        '''it's a hook for product_variant_multi advanced'''
        return True

    def _variant_name_get(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for product in self.browse(cr, uid, ids, context):
            model = product.variant_model_name
            r = map(lambda dim: [dim.dimension_id.sequence, model.replace('[NAME]', (dim.dimension_id.name or '')).replace('[VALUE]', dim.name or '-')], product.dimension_value_ids)
            r.sort()
            r = [x[1] for x in r]
            res[product.id] = (product.variant_model_name_separator or '').join(r)
        self.product_ids_variant_changed(cr, uid, ids, res, context=context)
        return res
        

    def _get_products_from_dimension(self, cr, uid, ids, context={}):
        result = []
        for type in self.pool.get('product.variant.dimension.type').browse(cr, uid, ids, context=context):
            for product_id in type.product_tmpl_id.variant_ids:
                result.append(product_id.id)
        return result

    def _get_products_from_product(self, cr, uid, ids, context={}):
        result = []
        for product in self.pool.get('product.product').browse(cr, uid, ids, context=context):
            # Checking if 'product_tmpl_id' is available, v6.0.1 gives error when a product is deleted
            if hasattr(product, 'product_tmpl_id'):
                for product_id in product.product_tmpl_id.variant_ids:
                    result.append(product_id.id)
        return result

    def _get_products_from_product_template(self, cr, uid, ids, context={}):
        return self.pool.get('product.template').get_products_from_product_template(cr, uid, ids, context=context)
    
    def _check_dimension_values(self, cr, uid, ids): # TODO: check that all dimension_types of the product_template have a corresponding dimension_value ??
        for p in self.browse(cr, uid, ids, {}):
            buffer = []
            for value in p.dimension_value_ids:
                buffer.append(value.dimension_id)
            unique_set = set(buffer)
            if len(unique_set) != len(buffer):
                return False
        return True

    def price_get(self, cr, uid, ids, ptype='list_price', context={}):
        result = super(product_product, self).price_get(cr, uid, ids, ptype, context)
        if ptype == 'list_price': #TODO check if the price_margin on the dimension is very usefull, maybe we will remove it
            product_uom_obj = self.pool.get('product.uom')
            for product in self.browse(cr, uid, ids, context=context):
                dimension_extra = 0.0
                for dim in product.dimension_value_ids:
                    dimension_extra += product.price_extra * dim.price_margin + dim.price_extra
                
                if 'uom' in context:
                    uom = product.uos_id or product.uom_id
                    dimension_extra = product_uom_obj._compute_price(cr, uid,
                            uom.id, dimension_extra, context['uom'])
                
                result[product.id] += dimension_extra

        elif ptype == 'standard_price':
            product_uom_obj = self.pool.get('product.uom')
            for product in self.browse(cr, uid, ids, context=context):
                dimension_extra = 0.0
                for dim in product.dimension_value_ids:
                    dimension_extra += product.cost_price_extra + dim.cost_price_extra
                
                if 'uom' in context:
                    uom = product.uos_id or product.uom_id
                    dimension_extra = product_uom_obj._compute_price(cr, uid,
                            uom.id, dimension_extra, context['uom'])
                
                result[product.id] += dimension_extra
                
        return result

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'variant_ids':False,})
        return super(product_product, self).copy(cr, uid, id, default, context)

    _columns = {
        'dimension_value_ids': fields.many2many('product.variant.dimension.value', 'product_product_dimension_rel', 'product_id','dimension_id', 'Dimensions', domain="[('product_tmpl_id','=',product_tmpl_id)]"),
        'cost_price_extra' : fields.float('Purchase Extra Cost', digits_compute=dp.get_precision('Purchase Price')),
        'variants': fields.function(_variant_name_get, method=True, type='char', size=128, string='Variants', readonly=True,
            store={
                'product.variant.dimension.type': (_get_products_from_dimension, None, 10),
                'product.product': (_get_products_from_product, ['product_tmpl_id', 'dimension_value_ids'], 10),
                'product.template': (_get_products_from_product_template, ['variant_model_name', 'variant_model_name_separator'], 10),
            }),
    }
    _constraints = [ (_check_dimension_values, 'Several dimension values for the same dimension type', ['dimension_value_ids']),]

product_product()
