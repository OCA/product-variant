# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2010-2013 Akretion (www.akretion.com). All Rights Reserved
#    @author Sebatien Beau <sebastien.beau@akretion.com>
#    @author Raphaël Valyi <raphael.valyi@akretion.com>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#    @author Chafique Delli <chafique.delli@akretion.com>
#    update to use a single "Generate/Update" button & price computation code
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

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
# Lib to eval python code with security
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
from collections import defaultdict
from mako.template import Template

import logging
_logger = logging.getLogger(__name__)

#
# Dimensions Definition
#
class product_variant_axe(orm.Model):
    _name = "product.variant.axe"
    _table = 'product_variant_axe'
    _inherits = {'attribute.attribute': 'product_attribute_id'}

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=None):
        if not context.get('product_tmpl_id', False):
            args = None
        return super(product_variant_axe, self).name_search(cr, user, '', args, 'ilike', None, None)

    _columns = {
        'sequence': fields.integer('Sequence', help=("The product 'variants' code will "
                                                     "use this to order the dimension values")),
        'allow_custom_value': fields.boolean('Allow Custom Value',
                                             help=("If true, custom values can be entered "
                                                   "in the product configurator")),
        'mandatory_dimension': fields.boolean('Mandatory Dimension',
                                              help=("If false, variant products will be created "
                                                    "with and without this dimension")),
        'product_attribute_id': fields.many2one('attribute.attribute', string='Product Attribute',
                                                required=True, ondelete='cascade'),
    }

    _defaults = {
        'mandatory_dimension': 1,
    }

    _order = "sequence"


class product_variant_dimension_value(orm.Model):
    _name = "product.variant.dimension.value"
    _description = "Dimension Value"

    #TODO
    #def unlink(self, cr, uid, ids, context=None):
    #    for value in self.browse(cr, uid, ids, context=context):
    #        if value.product_ids:
    #            product_names = [product.name for product in value.product_ids]
    #            product_list = '\n    - ' + '\n    - '.join(product_names)
    #            raise osv.except_osv(_('Dimension value can not be removed'),
    #                                 _("The value %s is used by the products : %s \n "
    #                                   "Please remove these products before removing the value.")
    #                                 % (value.option_id.name, product_list))
    #    return super(product_variant_dimension_value, self).unlink(cr, uid, ids, context)

    def _get_values_from_types(self, cr, uid, ids, context=None):
        dimvalue_obj = self.pool.get('product.variant.dimension.value')
        return dimvalue_obj.search(cr, uid, [('dimension_id', 'in', ids)], context=context)

    _columns = {
        #TODO option_id add param in context to have a full name 'dimension + option' exemple address on sale order
        'option_id' : fields.many2one('attribute.option', 'Option', required=True),
        'name': fields.related('option_id', 'name', type='char',
                               relation='product.variant.dimension.option',
                               string="Dimension Value", readonly=True),
        'sequence': fields.integer('Sequence'),
        'price_extra': fields.float('Sale Price Extra',
                                    digits_compute=dp.get_precision('Sale Price')),
        'price_margin': fields.float('Sale Price Margin',
                                     digits_compute=dp.get_precision('Sale Price')),
        'cost_price_extra': fields.float('Cost Price Extra',
                                         digits_compute=dp.get_precision('Purchase Price')),
        'dimension_id' : fields.many2one('product.variant.axe', 'Axe', required=True),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template',
                                           ondelete='cascade'),
        'dimension_sequence': fields.related('dimension_id', 'sequence', type='integer',
                                             relation='product.variant.dimension.type',
                                             #used for ordering purposes in the "variants"
                                             string="Related Dimension Sequence",
                                             store={'product.variant.dimension.type':
                                                    (_get_values_from_types, ['sequence'], 10)}),
        'active': fields.boolean('Active', help=("If false, this value will not be "
                                                 "used anymore to generate variants.")),
    }

    _defaults = {
        'active': True,
    }

    _sql_constraints = [('opt_dim_tmpl_uniq',
                        'UNIQUE(option_id, dimension_id, product_tmpl_id)',
                        _("The combination option and dimension type "
                          "already exists for this product template !")), ]

    _order = "dimension_sequence, sequence, option_id"


class product_template(orm.Model):
    _inherit = "product.template"

    _order = "name"

    _columns = {
        'name': fields.char('Name', size=128, translate=True, select=True, required=False),
        'axes_variance_ids':fields.many2many('product.variant.axe',
                                               'product_template_dimension_rel',
                                               'template_id', 'dimension_id', 'Dimension Types'),
        'value_ids': fields.one2many('product.variant.dimension.value',
                                     'product_tmpl_id',
                                     'Dimension Values'),
        'variant_ids': fields.one2many('product.product', 'product_tmpl_id', 'Variants'),
        'template_name': fields.char('Template Name', size=256, required=True,
                                          help=('Name in mako syntax in order to generate '
                                                'the name of your variant')),
        'template_code': fields.char('Template Code', size=256,
                                      help=('Code of the product in mako syntax')),
        'is_multi_variants': fields.boolean('Is Multi Variants'),
        'variant_track_production': fields.boolean('Track Production Lots on variants ?'),
        'variant_track_incoming': fields.boolean('Track Incoming Lots on variants ?'),
        'variant_track_outgoing': fields.boolean('Track Outgoing Lots on variants ?'),
        'do_not_update_variant': fields.boolean("Don't Update Variant"),
        'do_not_generate_new_variant': fields.boolean("Don't Generate New Variant"),
    }

    _defaults = {
        'template_name': '${" | ".join(["%s - %s" %(dimension.field_description, o[dimension.name].name) for dimension in o.axes_variance_ids])}',
        'is_multi_variants': False,
        'template_code': ('${"-".join([o[dimension.name].code for dimension in o.axes_variance_ids])}'),
    }

    def onchange_attribute_set(self, cr, uid, ids, attribute_set_id, context=None):
        location_obj = self.pool.get('attribute.location')
        axe_obj = self.pool.get('product.variant.axe')
        axes = []
        if attribute_set_id:
            attribute_ids = location_obj.search(cr, uid, [['attribute_set_id', '=', attribute_set_id]], context=context)
            for attribute in attribute_ids:
                axes_ids = axe_obj.search(cr, uid, [['product_attribute_id', '=', attribute]], context=context)
                if axes_ids:
                    axes.append(axes_ids[0])
        return  {'value' : {'axes_variance_ids' : axes}}

    def unlink(self, cr, uid, ids, context=None):
        if context and context.get('unlink_from_product_product', False):
            for template in self.browse(cr, uid, ids, context):
                if not template.is_multi_variants:
                    super(product_template, self).unlink(cr, uid, [template.id], context)
        else:
            for template in self.browse(cr, uid, ids, context):
                if template.variant_ids == []:
                    super(product_template, self).unlink(cr, uid, [template.id], context)
                else:
                    raise osv.except_osv(_("Cannot delete template"),
                                         _("This template has existing corresponding products..."))
        return True

    def add_all_option(self, cr, uid, ids, context=None):
        #Reactive all unactive values
        value_obj = self.pool.get('product.variant.dimension.value')
        for template in self.browse(cr, uid, ids, context=context):
            values_ids = value_obj.search(cr, uid, [['product_tmpl_id', '=', template.id],
                                                    '|', ['active', '=', False],
                                                         ['active', '=', True]], context=context)
            value_obj.write(cr, uid, values_ids,
                            {'active': True},
                            context=context)
            values = value_obj.browse(cr, uid, values_ids, context=context)
            existing_option_ids = [value.option_id.id for value in values]
            vals = {'value_ids': []}
            for dim in template.axes_variance_ids:
                for option in dim.option_ids:
                    if not option.id in existing_option_ids:
                        vals['value_ids'] += [[0, 0, {'dimension_id': dim.id, 'option_id': option.id}]]
            self.write(cr, uid, [template.id], vals, context=context)
        return True

    def get_products_from_product_template(self, cr, uid, ids, context=None):
        product_tmpl = self.read(cr, uid, ids, ['variant_ids'], context=context)
        return [id for vals in product_tmpl for id in vals['variant_ids']]

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'variant_ids': False, })
        new_id = super(product_template, self).copy(cr, uid, id, default, context)

        val_obj = self.pool.get('product.variant.dimension.value')
        template = self.read(cr, uid, new_id, ['value_ids'], context=context)
        # Making sure the values we duplicated are no longer linked via the
        # m2m 'product_ids' with the product.product variants from the original template
        val_obj.write(cr, uid, template['value_ids'], {
            'product_ids': [(6, 0, [])],
        }, context=context)

        return new_id

    def copy_translations(self, cr, uid, old_id, new_id, context=None):
        if context is None:
            context = {}
        # avoid recursion through already copied records in case of circular relationship
        seen_map = context.setdefault('__copy_translations_seen', {})
        if old_id in seen_map.setdefault(self._name, []):
            return
        seen_map[self._name].append(old_id)
        return super(product_template, self).copy_translations(cr, uid, old_id, new_id,
                                                               context=context)

    def _create_variant_list(self, cr, ids, uid, vals, context=None):

        def cartesian_product(args):
            if len(args) == 1:
                return [x and [x] or [] for x in args[0]]
            return [(i and [i] or []) + j for j in cartesian_product(args[1:]) for i in args[0]]

        return cartesian_product(vals)

    def button_generate_variants(self, cr, uid, ids, context=None):
        variants_obj = self.pool.get('product.product')
        option_obj = self.pool['attribute.option']

        for product_temp in self.browse(cr, uid, ids, context):
            res = defaultdict(list)
            for value in product_temp.value_ids:
                res[value.dimension_id].append(value.option_id.id)

            temp_val_list = []
            dimension_fields = []
            for dim in res:
                dimension_fields.append(dim.name)
                temp_val_list += [res[dim] + (not dim.mandatory_dimension and [None] or [])]


            #example temp_val_list is equal to [['red', 'blue', 'yellow'], ['L', 'XL', 'M']]
            #In reallity it's not a string value but the id of the value

            existing_product_ids = variants_obj.search(cr, uid,
                                                       [('product_tmpl_id', '=', product_temp.id)])
            created_product_ids = []
            if temp_val_list and not product_temp.do_not_generate_new_variant:
                list_of_combinaison= self._create_variant_list(cr, uid, ids, temp_val_list, context)
                existing_products = variants_obj.read(cr, uid, existing_product_ids,
                                                               dimension_fields, context=context)
                list_of_existing_combinaison = []
                for existing_product in existing_products:
                    existing_combinaison = []
                    for field in dimension_fields:
                        existing_combinaison.append(existing_product[field][0])
                    list_of_existing_combinaison.append(existing_combinaison)

                list_of_combinaison_to_create = [x for x in list_of_combinaison
                                              if not x in list_of_existing_combinaison]

                _logger.debug("variant existing : %s, variant to create : %s",
                              len(list_of_existing_combinaison),
                              len(list_of_combinaison_to_create))
                count = 0
                for combinaison in list_of_combinaison_to_create:
                    count += 1
                    vals = {
                        'name': product_temp.name,
                        'track_production': product_temp.variant_track_production,
                        'track_incoming': product_temp.variant_track_incoming,
                        'track_outgoing': product_temp.variant_track_outgoing,
                        'product_tmpl_id': product_temp.id,
                    }

                    for option in option_obj.browse(cr, uid, combinaison, context=context):
                        vals[option.attribute_id.name] = option.id

                    cr.execute("SAVEPOINT pre_variant_save")
                    try:
                        product_id = variants_obj.create(cr, uid, vals,
                                                         {'generate_from_template': True})
                        created_product_ids.append(product_id)
                        if count % 50 == 0:
                            _logger.debug("product created : %s", count)
                    except Exception, e:
                        _logger.error("Error creating product variant: %s",
                                      e, exc_info=True)
                        _logger.debug("Values used to attempt creation of product variant: %s",
                                      vals)
                        cr.execute("ROLLBACK TO SAVEPOINT pre_variant_save")
                    cr.execute("RELEASE SAVEPOINT pre_variant_save")

                _logger.debug("product created : %s", count)

            if not product_temp.do_not_update_variant:
                product_ids = existing_product_ids + created_product_ids
            else:
                product_ids = created_product_ids

            # FIRST, Generate/Update variant names ('variants' field)
            _logger.debug("Starting to generate/update variant names...")
            self.pool.get('product.product').update_variant(cr, uid, product_ids,
                                                                 context=context)
            #_logger.debug("End of the generation/update of variant names.")
            ## SECOND, Generate/Update product codes and properties (we may need variants name)
            #_logger.debug("Starting to generate/update product codes and properties...")
            #self.pool.get('product.product').build_product_code_and_properties(cr, uid,
            #                                                                   product_ids,
            #                                                                   context=context)
            #_logger.debug("End of the generation/update of product codes and properties.")
            ## THIRD, Generate/Update product names (we may need variants name for that)
            #_logger.debug("Starting to generate/update product names...")
            #self.pool.get('product.product').build_product_name(cr, uid, product_ids,
            #                                                    context=context)
            #_logger.debug("End of generation/update of product names.")
        return True


class product_product(orm.Model):
    _inherit = "product.product"

    def init(self, cr):
        #TODO do it only for the first installation
        #For the first installation if you already have product in your database,
        # the name of the existing product will be empty, so we fill it
        cr.execute("update product_product set name=name_template where name is null;")
        return True

    def unlink(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        context['unlink_from_product_product'] = True
        return super(product_product, self).unlink(cr, uid, ids, context)

    def update_variant(self, cr, uid, ids, context=None):
        obj_lang = self.pool.get('res.lang')
        lang_ids = obj_lang.search(cr, uid, [('translatable', '=', True)], context=context)
        lang_code = [x['code']
                     for x in obj_lang.read(cr, uid, lang_ids, ['code'], context=context)]
        for code in lang_code:
            context['lang'] = code
            for product in self.browse(cr, uid, ids, context=context):
                self._update_variant(cr, uid, product, context=context)
        return True

    def _update_variant(self, cr, uid, product, context=None):
        vals = self._prepare_update_vals(cr, uid, product, context=context)
        vals = self._remove_not_updated(cr, uid, product, vals, context=context)
        if vals:
            product.write(vals)
        return True

    def _prepare_update_vals(self, cr, uid, product, context=None):
        context['is_multi_variants'] = True
        vals = {
            'variants': Template(product.template_name).render(o=product),
            'default_code': Template(product.template_code).render(o=product),
        }
        vals['name'] = (product.product_tmpl_id.name or '')+ ' ' + vals['variants']

        return vals

    def _remove_not_updated(self, cr, uid, product, vals, context=None):
        vals_to_write = {}
        for key in vals:
            if vals[key] != product[key]:
                vals_to_write[key] = vals[key]
        return vals_to_write

    _columns = {
        'name': fields.char('Name', size=128, translate=True, select=True),
        'variants': fields.char('Variants', size=128),
    }