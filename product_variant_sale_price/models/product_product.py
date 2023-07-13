# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_fix_price(self, vals):
        if "list_price" in vals:
            self.mapped("product_variant_ids").write({"fix_price": vals["list_price"]})

    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for i, product_tmpl in enumerate(records):
            single_vals = vals[i] if isinstance(vals, list) else vals
            product_tmpl._update_fix_price(single_vals)
        return records

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("skip_update_fix_price", False):
            return res
        for template in self:
            template._update_fix_price(vals)
        return res

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1,
        pricelist=False,
        parent_combination=False,
        only_template=False,
    ):
        res = super()._get_combination_info(
            combination,
            product_id,
            add_qty,
            pricelist,
            parent_combination,
            only_template,
        )
        res["price_extra"] = 0.0
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    lst_price = fields.Float(
        compute="_compute_lst_price",
        inverse="_inverse_product_lst_price",
    )
    list_price = fields.Float(
        compute="_compute_list_price",
    )
    fix_price = fields.Float()

    @api.depends("fix_price")
    def _compute_lst_price(self):
        uom_model = self.env["uom.uom"]
        for product in self:
            price = product.fix_price or product.list_price
            if self.env.context.get("uom"):
                context_uom = uom_model.browse(self.env.context["uom"])
                price = product.uom_id._compute_price(price, context_uom)
            product.lst_price = price

    def _compute_list_price(self):
        uom_model = self.env["uom.uom"]
        for product in self:
            price = product.fix_price or product.product_tmpl_id.list_price
            if self.env.context.get("uom"):
                context_uom = uom_model.browse(self.env.context["uom"])
                price = product.uom_id._compute_price(price, context_uom)
            product.list_price = price

    def _inverse_product_lst_price(self):
        uom_model = self.env["uom.uom"]
        for product in self:
            vals = {}
            if self.env.context.get("uom"):
                vals["fix_price"] = product.uom_id._compute_price(
                    product.lst_price, uom_model.browse(self.env.context["uom"])
                )
            else:
                vals["fix_price"] = product.lst_price
            if product.product_variant_count == 1:
                product.product_tmpl_id.list_price = vals["fix_price"]
            else:
                other_products = product.product_tmpl_id.product_variant_ids - product
                fix_prices = other_products.mapped("fix_price") + [product.lst_price]
                # for consistency with price shown in the shop
                product.product_tmpl_id.with_context(
                    skip_update_fix_price=True
                ).list_price = min(fix_prices)
            product.write(vals)

    def _compute_product_price_extra(self):
        """the sale.order.line module calculates the price_unit by adding
        the value of price_extra and this can generate inconsistencies
        if the field has old data stored."""
        for product in self:
            product.price_extra = 0.0
