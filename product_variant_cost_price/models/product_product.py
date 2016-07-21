# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# © 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _get_selection_cost_method(self):
        return self.env['product.template'].fields_get(
            allfields=['cost_method'])['cost_method']['selection']

    @api.model
    def _set_standard_price(self, product, value):
        """Store the standard price change in order to be able to retrieve the
        cost of a product variant for a given date
        """
        # With this, we make sure everyone can record the history
        # independently from its ACL
        price_history_obj = self.env['product.price.history.product'].sudo()
        user_company = self.env.user.company_id.id
        company_id = self.env.context.get('force_company', user_company)
        price_history_obj.create({
            'product_id': product.id,
            'product_template_id': product.product_tmpl_id.id,
            'cost': value,
            'company_id': company_id,
        })
        # Save the value in the template if there's only one variant.
        template = product.product_tmpl_id
        if template.product_variant_count == 1:
            template.with_context(bypass_down_write=1).standard_price = value

    standard_price = fields.Float(
        string='Cost Price', digits=dp.get_precision('Product Price'),
        help="Cost price of the product variant used for standard "
        "stock valuation in accounting and used as a base price on purchase "
        "orders. Expressed in the default unit of measure of the product.",
        groups="base.group_user", company_dependent=True)
    cost_method = fields.Selection(
        string="Costing Method", selection='_get_selection_cost_method',
        help="Standard Price: The cost price is manually updated at the end "
             "of a specific period (usually every year).\n"
             "Average Price: The cost price is recomputed at each incoming "
             "shipment and used for the product valuation.\n"
             "Real Price: The cost price displayed is the price of the last "
             "outgoing product (will be use in case of inventory loss for "
             "example).",
        required=True, copy=True, company_dependent=True)

    @api.model
    def create(self, values):
        if 'product_tmpl_id' in values and 'standard_price' not in values:
            template = self.env['product.template'].browse(
                values.get('product_tmpl_id'))
            values.update({
                'standard_price': template.standard_price,
            })
        product = super(ProductProduct, self).create(values)
        self._set_standard_price(product, values.get('standard_price', 0.0))
        return product

    @api.multi
    def write(self, values):
        if 'standard_price' in values:
            for product in self:
                product._set_standard_price(product, values['standard_price'])
        if (values.get('cost_method', False) and not
                self.env.context.get('force_not_load', False)):
            cost_method = values.get('cost_method', False)
            templates = self.mapped('product_tmpl_id').filtered(
                lambda x: len(x.product_variant_ids) == 1 and
                x.cost_method != cost_method)
            templates.with_context(force_not_load=True).write(
                {'cost_method': cost_method})
        return super(ProductProduct, self).write(values)


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'
    _name = 'product.price.history.product'

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', ondelete='cascade')
