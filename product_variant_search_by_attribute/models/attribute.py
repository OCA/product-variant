# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, models


_logger = logging.getLogger(__name__)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.multi
    def write(self, vals):
        """ Attribute Values update impact products: we take care
            to propagate changes on attribute_str field"""
        res = super(ProductAttributeValue, self).write(vals)
        if 'name' in vals:
            sql = """SELECT prod_id
                     FROM product_attribute_value_product_product_rel
                     WHERE att_id = %s""" % self.id
            self._cr.execute(sql)
            product_ids = self._cr.fetchall()  # [(99999), (...)]
            if product_ids:
                product_ids = [x[0] for x in product_ids]
                products = self.env['product.product'].browse(product_ids)
                _logger.debug(" >>> '%s' products to update after attribute "
                              "('%s') modified" % (len(product_ids), self.id))
                products._compute_attrib_str_after_attrib_value_change()
                _logger.debug(" >>> '%s' products update done")
        return res
