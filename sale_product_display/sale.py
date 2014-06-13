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

from openerp.osv import orm, osv
from openerp.tools.translate import _


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'


    def _check_product_display(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.product_id.is_display:
                raise osv.except_osv(_('Error'), _('You cannot validate the order with product display %s.')% (record.product_id.name))
        return True

    _constraints = [
        (_check_product_display, 'You cannot validate an order with a product display.',
            [])]
