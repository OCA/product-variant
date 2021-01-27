# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """Create possible product variants not yet created."""
        lines_without_product = self.mapped("order_line").filtered(
            lambda x: not x.product_id and x.product_tmpl_id
        )
        for line in lines_without_product:
            line.create_variant_if_needed()
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.configurator"]
    _name = "sale.order.line"

    product_tmpl_id = fields.Many2one(
        store=True,
        readonly=False,
        related=False,
        string="Product Template (no related)",
    )
    product_id = fields.Many2one(required=False)

    _sql_constraints = [
        (
            "accountable_required_fields",
            "CHECK(display_type IS NOT NULL OR "
            "((product_id IS NOT NULL OR product_tmpl_id IS NOT NULL) AND "
            "product_uom IS NOT NULL))",
            "Missing required fields on accountable sale order line.",
        ),
        (
            "non_accountable_null_fields",
            "CHECK(display_type IS NULL OR "
            "(product_id IS NULL AND product_tmpl_id IS NULL AND "
            "price_unit = 0 AND product_uom_qty = 0 AND "
            "product_uom IS NULL AND customer_lead = 0))",
            "Forbidden values on non-accountable sale order line",
        ),
    ]

    @api.model
    def create(self, vals):
        """Create product if not exist when the sales order is already
        confirmed and a line is added.
        """
        if vals.get("order_id") and not vals.get("product_id"):
            order = self.env["sale.order"].browse(vals["order_id"])
            if order.state == "sale":
                line = self.new(vals)
                product = line.create_variant_if_needed()
                vals["product_id"] = product.id
        return super().create(vals)

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id_configurator(self):
        res = super()._onchange_product_tmpl_id_configurator()
        if self.product_tmpl_id.attribute_line_ids:
            domain = res.setdefault("domain", {})
            domain["product_uom"] = [
                ("category_id", "=", self.product_tmpl_id.uom_id.category_id.id),
            ]
            self.product_uom = self.product_tmpl_id.uom_id
            self.price_unit = self.order_id.pricelist_id.with_context(
                {"uom": self.product_uom.id, "date": self.order_id.date_order}
            ).template_price_get(
                self.product_tmpl_id.id,
                self.product_uom_qty or 1.0,
                self.order_id.partner_id.id,
            )[
                self.order_id.pricelist_id.id
            ]
        # Update taxes
        fpos = (
            self.order_id.fiscal_position_id
            or self.order_id.partner_id.property_account_position_id
        )
        # If company_id is set, always filter taxes by the company
        taxes = self.product_tmpl_id.taxes_id.filtered(
            lambda r: not self.company_id or r.company_id == self.company_id
        )
        self.tax_id = fpos.map_tax(taxes) if fpos else taxes
        product_tmpl = self.product_tmpl_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )
        # product_configurator methods don't take into account this description
        if product_tmpl.description_sale:
            self.name = (self.name or "") + "\n" + product_tmpl.description_sale
        if self.order_id.pricelist_id and self.order_id.partner_id:
            self.price_unit = self.env["account.tax"]._fix_tax_included_price(
                product_tmpl.price, product_tmpl.taxes_id, self.tax_id,
            )
        return res

    @api.onchange("product_id")
    def product_id_change(self):
        """Call again the configurator onchange after this main onchange
        for making sure the SO line description is correct.
        """
        res = super().product_id_change()
        self._onchange_product_id_configurator()
        # product_configurator methods don't take into account this description
        if self.product_id.description_sale:
            self.name = (self.name or "") + "\n" + self.product_id.description_sale
        return res

    def _update_price_configurator(self):
        """If there are enough data (template, pricelist & partner), check new
        price and update line if different.
        """
        self.ensure_one()
        if (
            not self.product_tmpl_id
            or not self.order_id.pricelist_id
            or not self.order_id.partner_id
        ):
            return
        product_tmpl = self.product_tmpl_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date_order=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get("fiscal_position"),
        )
        price = self.env["account.tax"]._fix_tax_included_price(
            self.price_extra + self._get_display_price(product_tmpl),
            product_tmpl.taxes_id,
            self.tax_id,
        )
        if self.price_unit != price:
            self.price_unit = price

    @api.onchange("product_attribute_ids")
    def _onchange_product_attribute_ids_configurator(self):
        """Update price for having into account possible extra prices"""
        res = super()._onchange_product_attribute_ids_configurator()
        self._update_price_configurator()
        return res

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        """Update price for having into account changes due to qty"""
        res = super().product_uom_change()
        if not self.product_id:
            self._update_price_configurator()
        return res
