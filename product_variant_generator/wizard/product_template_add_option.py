# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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


class ProductTemplateAddOption(orm.TransientModel):
    _name = 'product.template.add.option'
    _description = 'Product Template Add Option'

    def _get_option_domain(self, cr, uid, tmpl, context=None):
        domain = [('attribute_id', 'in', [x.id for x in tmpl.dimension_ids])]
        existing_option_ids = [value.option_id.id for value in tmpl.value_ids]
        if existing_option_ids:
            domain.append(('id', 'not in', existing_option_ids))
        return domain

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(ProductTemplateAddOption, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu,
            )
        tmpl_id = context.get('active_id')
        if tmpl_id and view_type == 'form':
            tmpl_obj = self.pool['product.template']
            tmpl = tmpl_obj.browse(cr, uid, tmpl_id, context=context)
            res['fields']['option_ids']['domain'] = self._get_option_domain(
                cr, uid, tmpl, context=context)
        return res

    _columns = {
        'option_ids': fields.many2many(
            'attribute.option',
            string='Option'),
    }

    def add_option(self, cr, uid, ids, context=None):
        tmpl_obj = self.pool['product.template']
        for wizard in self.browse(cr, uid, ids, context=context):
            values = []
            for option in wizard.option_ids:
                values.append([0, 0, {
                    'dimension_id': option.attribute_id.id,
                    'option_id': option.id,
                    }])
            tmpl_obj.write(cr, uid, context['active_id'], {
                'value_ids': values,
                }, context=context)
        return True
