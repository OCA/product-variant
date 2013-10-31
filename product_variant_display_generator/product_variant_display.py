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

import logging
_logger = logging.getLogger(__name__)


#class product_product(orm.Model):
#    _inherit = "product.product"
#
#    def _prepare_update_vals(self, cr, uid, product, context=None):
#        context['is_multi_variants'] = True
#        vals = {
#            'variants': Template(product.template_name).render(o=product),
#            'default_code': Template(product.template_code).render(o=product),
#            }
#        if product.is_displays:
#            vals['name'] = (product.product_ids.name or '') + ' ' + vals['variants']
#        else:
#            vals['name'] = (product.product_tmpl_id.name or '') + ' ' + vals['variants']
#        return vals


class product_template(orm.Model):
    _inherit = "product.template"

