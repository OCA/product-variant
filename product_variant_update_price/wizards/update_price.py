# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from openerp import models, api, fields


class ProductUpdatePrice(models.TransientModel):
    _name = "product.update.price"
    _description = "Allow to update sale price"

    percentage = fields.Float(
        required=True,
        help="Sale price percentage increase")

    @api.multi
    def update_price(self):
        self.ensure_one()
        product_ids = self.env.context.get('active_ids')
        products = self.env['product.template'].browse(product_ids)
        if self.percentage:
            attr_prices = self._get_attribute_prices(products)
            for product in products:
                # update list_price
                new_price = compute_price(product.list_price, self.percentage)
                product.write({'list_price': new_price})
                # update price_extra
                for record, price_extra in attr_prices[product].items():
                    new_price = compute_price(price_extra, self.percentage)
                    record.write({'price_extra': new_price})

    @api.model
    def _get_attribute_prices(self, products):
        prices = defaultdict(dict)
        attr_prices = self.env['product.attribute.price'].search([
            ('product_tmpl_id', 'in', products._ids)])
        for price in attr_prices:
            prices[price.product_tmpl_id].update({price: price.price_extra})
        return prices


def compute_price(initial_value, percentage):
    """ Increase or decrease price according to percentage
        of the initial value
    """
    return initial_value + percentage * initial_value / 100
