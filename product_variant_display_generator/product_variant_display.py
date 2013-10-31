# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2013 Akretion (http://www.akretion.com).
#   @author Chafique Delli <chafique.delli@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
from collections import defaultdict
from mako.template import Template

import logging
_logger = logging.getLogger(__name__)


class product_product(orm.Model):
    _inherit = "product.product"

    def _prepare_update_vals(self, cr, uid, product, context=None):
        context['is_multi_variants'] = True
        vals = {
            'variants': Template(product.template_name).render(o=product),
            'default_code': Template(product.template_code).render(o=product),
            }
        if product.is_displays:
            vals['name'] = (product.product_ids.name or '') + ' ' + vals['variants']
        else:
            vals['name'] = (product.product_tmpl_id.name or '') + ' ' + vals['variants']
        return vals


class product_template(orm.Model):
    _inherit = "product.template"

    def button_generate_variants(self, cr, uid, ids, context=None):
        display_obj = self.pool.get('product.display')
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
                list_of_combinaison = self._create_variant_list(cr, uid,
                                                                ids, temp_val_list,
                                                                context)
                existing_products = variants_obj.read(cr, uid,
                                                      existing_product_ids,
                                                      dimension_fields,
                                                      context=context)
                list_of_existing_combinaison = []
                for existing_product in existing_products:
                    existing_combinaison = []
                    for field in dimension_fields:
                        if existing_product[field]:
                            existing_combinaison.append(existing_product[field][0])
                        else:
                            existing_combinaison.append(None)
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

                    for option in option_obj.browse(cr, uid,
                                                    combinaison, context=context):
                        vals[option.attribute_id.name] = option.id

                    cr.execute("SAVEPOINT pre_variant_save")
                    try:
                        product_id = variants_obj.create(cr, uid, vals,
                                                         {'generate_from_template': True})
                        if product_temp.is_displays:
                            vals = {
                                'name': product_temp.product_ids.name,
                                'product_ids': product_temp.product_ids.id,
                                'type': product_temp.type,
                                }
                            for option in option_obj.browse(cr, uid,
                                                    combinaison, context=context):
                                vals['attribute_ids'] = option.attribute_id.id
                                vals['attribute_options'] = option.id
                            display_obj.create(cr, uid, vals,
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
            variants_obj.update_variant(cr, uid, product_ids, context=context)
        return True
