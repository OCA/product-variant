# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _product_from_tmpl(self):
        """ Creates a product in memory from template to use its methods """
        return self.env['product.product'].new({
            'product_tmpl_id': self.id,
            'name': self.name,
        })
