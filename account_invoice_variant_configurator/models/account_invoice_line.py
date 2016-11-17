# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class AccountInvoiceLine(models.Model):

    _inherit = ['account.invoice.line', 'product.configurator']
    _name = 'account.invoice.line'
