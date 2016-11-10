# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import itertools
import logging

from openerp import api, fields, models


_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    attribute_str = fields.Char(
        string='Attribute string', compute='_compute_attribute_str',
        store=True, index=True,
        help="Store all attribute values. Required to search variants "
             "from attributes")

    @api.multi
    @api.depends('attribute_value_ids', 'active')
    def _compute_attribute_str(self):
        for prd in self:
            if prd.attribute_value_ids:
                attrs = [x.name.lower() for x in prd.attribute_value_ids]
                prd.attribute_str = u' '.join(attrs)

    @api.multi
    def _compute_attrib_str_after_attrib_value_change(self):
        """ This method is called when you modified attribute value name
            on impacted products: in this case you may have a huge data volume
        """
        sql = ''
        product_ids = [x.id for x in self]
        self._cr.execute(self._get_product_info_query(), (tuple(product_ids),))
        product_infos = self._cr.fetchall()
        products_map = {x[0]: x[1] for x in product_infos}
        update_statement = "UPDATE product_product SET attribute_str = " \
                           "%(info)s WHERE id = %(id)s;"
        for prd in self:
            if products_map.get(prd.id):
                # We do not use previous method compute_attribute_str()
                # for performance reason: ie 30 000 products to update
                #     5 seconds with this method
                #  or 3 minutes for _compute_attribute_str() method above
                query_params = {'info': products_map[prd.id], 'id': prd.id}
                sql += self._cr.mogrify(update_statement, query_params)
        if sql:
            self._cr.execute(sql)
            self.env.invalidate_all()

    def _get_product_info_query(self):
        """ You may customize aggregate string according to your needs """
        return """
            SELECT re.prod_id as id, lower(string_agg(pa.name, ' ')) as string
            FROM product_attribute_value_product_product_rel re
               LEFT JOIN product_attribute_value pa ON pa.id = re.att_id
            WHERE re.prod_id in %s
            GROUP BY 1 """

    def search(self, cr, uid, domain, offset=0, limit=None,
               order=None, context=None, count=False):
        _logger.debug('Initial domain search %s' % domain)
        separator = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'search.by.attribute.separator', ' ')
        domain = self.domain_replacement(domain, 'attribute_str', separator)
        return super(ProductProduct, self).search(
            cr, uid, domain, offset=offset, limit=limit, order=order,
            context=context, count=count)

    def domain_replacement(self, domain, field, separator):
        """ convert [expr1, expr2, expr3] in [expr1, expr2a, expr2b, expr3]
            according to expr => (field, 'ilike', mystring)
        """
        position = 0
        domain_idx = []
        for arg in domain:
            # we track position of field in domain
            if tuple(arg)[0] == field:
                domain_idx.append(position)
            position += 1
        for position in reversed(domain_idx):
            modified_domain = True
            clauses = self.domain_split(domain[position][2], field, separator)
            for clause in clauses:
                domain.insert(position, clause)
            # we remove initial expression with this field
            del domain[position + len(clauses)]
            if modified_domain:
                _logger.debug('Modified domain attr. %s' % domain)
        return domain

    def domain_split(self, value, field, separator):
        """ convert this string 'first second third' in this list
            ['&', '&',
             ('myfield', 'like', 'first'),
             ('myfield', 'like', 'second'),
             ('myfield', 'like', 'third')]
        """
        words = value.lower().split(separator)
        # we create as many expression as words in this field
        clauses = [[field, 'like', word] for word in words]
        if len(clauses) > 1:
            # we need explicit operator '&' to be compatible
            # with complex domains using '|' operator
            operators = list(itertools.repeat('&', len(clauses) - 1))
            clauses = clauses + operators
        return clauses
