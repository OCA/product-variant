# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models


class PurchaseOrderLine(models.Model):
    _inherit = ['purchase.order.line', 'product.configurator']
    _name = 'purchase.order.line'
