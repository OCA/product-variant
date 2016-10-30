# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductConfiguratorAttribute(models.Model):
    _name = 'product.configurator.attribute'

    owner_model = fields.Char(required=True)

    owner_id = fields.Integer(string="Owner",
                              required=True,
                              ondelete="cascade")
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True)
    attribute_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Attribute',
        readonly=True)
    value_id = fields.Many2one(
        comodel_name='product.attribute.value',
        domain="[('attribute_id', '=', attribute_id)]",
        string='Value')

    price_extra = fields.Float(
        compute='_compute_price_extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with this attribute "
             "value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")

    @api.onchange('attribute_id')
    def onchange_attribute_id(self):
        if self.attribute_id and self.product_tmpl_id:
            attribute = self.product_tmpl_id.attribute_line_ids.filtered(
                lambda rec: rec.attribute_id == self.attribute_id
            )
            possible_value_ids = attribute.value_ids.sorted()
            return {
                'domain': {'value_id':
                           [('attribute_id', '=', self.attribute_id.id),
                            ('id', 'in', possible_value_ids[0][2])]}}

    @api.depends('value_id')
    def _compute_price_extra(self):
        for record in self:
            record.price_extra = sum(
                record.value_id.price_ids.filtered(
                    lambda x: (
                        x.product_tmpl_id == record.product_tmpl_id)
                ).mapped('price_extra'))
