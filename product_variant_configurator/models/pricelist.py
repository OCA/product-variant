# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(self, products, qty, uom=None, date=False, **kwargs):
        """Overwrite for covering the case where templates are passed and a
        different uom is used."""
        if products._name != "product.template":
            # Standard use case - Nothing to do
            return super(ProductPricelist, self)._compute_price_rule(
                products,
                qty,
                date=date,
                uom=uom,
            )
        # Isolate object
        pricelist_obj = self

        if not uom and pricelist_obj.env.context.get("uom"):
            ctx = dict(pricelist_obj.env.context)
            # Remove uom context for avoiding the re-processing
            pricelist_obj = pricelist_obj.with_context(**ctx)

        return super(ProductPricelist, pricelist_obj)._compute_price_rule(
            products,
            qty,
            date=date,
            uom=False,
        )

    def template_price_get(self, prod_id, qty, partner=None):
        return {
            key: price[0]
            for key, price in self.template_price_rule_get(
                prod_id, qty, partner=partner
            ).items()
        }

    def template_price_rule_get(self, prod_id, qty, partner=None):
        return self._compute_price_rule_multi(prod_id, qty)[prod_id.id]
