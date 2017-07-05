# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def _select_seller(self, partner_id=False, quantity=0.0, date=None,
                       uom_id=False):
        """ Make use of ProductProduct _select_seller method """
        self.ensure_one()
        product = self._product_from_tmpl()
        return product._select_seller(
            partner_id=partner_id, quantity=quantity, date=date, uom_id=uom_id,
        )

    def _product_from_tmpl(self):
        """ Creates a product in memory from template to use its methods """
        return self.env['product.product'].new({
            'product_tmpl_id': self.id,
            'name': self.name,
        })
