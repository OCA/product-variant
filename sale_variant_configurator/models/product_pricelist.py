# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def get_product_price_rule(self, product, quantity, partner, date=False,
                               uom_id=False):
        self.ensure_one()
        # If sale pricelist has a discount policy equal to 'without_discount'
        # an error is raised because product_id is null
        if not product and self.env.context.get('product_id'):
            product = self.env.context.get('product_id')
        return self._compute_price_rule([(product, quantity, partner)],
                                        date=date, uom_id=uom_id)[product.id]
