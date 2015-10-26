# -*- coding: utf-8 -*-
# (c) 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_selection_cost_method(self):
        return self.env['product.template'].fields_get(
            allfields=['cost_method'])['cost_method']['selection']

    def default_cost_method(self):
        default_dict = self.env['product.template'].default_get(
            ['cost_method'])
        return default_dict.get('cost_method')

    @api.model
    def _set_standard_price(self, product, value):
        '''
        Store the standard price change in order to be able to retrieve the
        cost of a product variant for a given date
        '''
        price_history_obj = self.env['product.price.history']
        user_company = self.env.user.company_id.id
        company_id = self.env.context.get('force_company', user_company)
        price_history_obj.create({
            'product_id': product.id,
            'product_template_id': product.product_tmpl_id.id,
            'cost': value,
            'company_id': company_id,
        })

    standard_price = fields.Float(
        string='Cost Price', digits=dp.get_precision('Product Price'),
        help="Cost price of the product variant used for standard "
        "stock valuation in accounting and used as a base price on purchase "
        "orders. Expressed in the default unit of measure of the product.",
        groups="base.group_user", company_dependent=True)
    cost_method = fields.Selection(
        string="Costing Method", selection='_get_selection_cost_method',
        help="""Standard Price: The cost price is manually updated at the end
                of a specific period (usually every year).
                Average Price: The cost price is recomputed at each incoming
                shipment and used for the product valuation.
                Real Price: The cost price displayed is the price of the last
                outgoing product (will be use in case of inventory loss for
                example).""",
        required=True, copy=True, company_dependent=True,
        default='default_cost_method')

    @api.model
    def create(self, values):
        product = super(ProductProduct, self).create(values)
        self._set_standard_price(product, values.get('standard_price', 0.0))
        return product

    @api.multi
    def write(self, values):
        if 'standard_price' in values:
            for product in self:
                product._set_standard_price(product, values['standard_price'])
        return super(ProductProduct, self).write(values)


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', ondelete='cascade')
