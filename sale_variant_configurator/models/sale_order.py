# -*- coding: utf-8 -*-
# © 2014-2016 Oihane Crucelaegui - AvanzOSC
# © 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """Avoid to have 2 times the field product_tmpl_id, as modules like
        sale_stock adds this field as invisible, so we can't trust the order
        of them. We also override the modifiers to avoid a readonly field.
        """
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type != 'form':
            return res  # pragma: no cover
        if 'order_line' not in res['fields']:
            return res  # pragma: no cover
        line_field = res['fields']['order_line']
        if 'form' not in line_field['views']:
            return res  # pragma: no cover
        view = line_field['views']['form']
        eview = etree.fromstring(view['arch'])
        fields = eview.xpath("//field[@name='product_tmpl_id']")
        field_added = False
        for field in fields:
            if field.get('invisible') or field_added:
                field.getparent().remove(field)
            else:
                # Remove modifiers that makes the field readonly
                field.set('modifiers', "")
                field_added = True
        view['arch'] = etree.tostring(eview)
        return res

    @api.multi
    def action_confirm(self):
        """Create possible product variants not yet created."""
        lines_without_product = self.mapped('order_line').filtered(
            lambda x: not x.product_id and x.product_tmpl_id
        )
        for line in lines_without_product:
            line.create_variant_if_needed()
        return super(SaleOrder, self).action_confirm()


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.configurator"]
    _name = "sale.order.line"

    product_tmpl_id = fields.Many2one(store=True, readonly=False,
                                      related=False)
    product_id = fields.Many2one(required=False)
    # this is for getting the proper language for product description
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        related='order_id.partner_id',
        readonly=True,
    )

    @api.model
    def create(self, vals):
        """Create product if not exist when the sales order is already
        confirmed and a line is added.
        """
        if vals.get('order_id') and not vals.get('product_id'):
            order = self.env['sale.order'].browse(vals['order_id'])
            if order.state == 'sale':
                line = self.new(vals)
                product = line.create_variant_if_needed()
                vals['product_id'] = product.id
        return super(SaleOrderLine, self).create(vals)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id_configurator(self):
        res = super(
            SaleOrderLine, self,
        )._onchange_product_tmpl_id_configurator()
        if self.product_tmpl_id.attribute_line_ids:
            domain = res.setdefault('domain', {})
            domain['product_uom'] = [
                ('category_id', '=',
                 self.product_tmpl_id.uom_id.category_id.id),
            ]
            self.product_uom = self.product_tmpl_id.uom_id
            self.price_unit = self.order_id.pricelist_id.with_context(
                {'uom': self.product_uom.id,
                 'date': self.order_id.date_order}).template_price_get(
                self.product_tmpl_id.id, self.product_uom_qty or 1.0,
                self.order_id.partner_id.id)[self.order_id.pricelist_id.id]
        # Update taxes
        fpos = (self.order_id.fiscal_position_id or
                self.order_id.partner_id.property_account_position_id)
        # If company_id is set, always filter taxes by the company
        taxes = self.product_tmpl_id.taxes_id.filtered(
            lambda r: not self.company_id or r.company_id == self.company_id
        )
        self.tax_id = fpos.map_tax(taxes) if fpos else taxes
        product_tmpl = self.product_tmpl_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )
        # product_configurator methods don't take into account this description
        if product_tmpl.description_sale:
            self.name = (
                (self.name or '') + '\n' + product_tmpl.description_sale
            )
        if self.order_id.pricelist_id and self.order_id.partner_id:
            self.price_unit = self.env['account.tax']._fix_tax_included_price(
                product_tmpl.price, product_tmpl.taxes_id, self.tax_id,
            )
        return res

    @api.onchange('product_id')
    def product_id_change(self):
        """Call again the configurator onchange after this main onchange
        for making sure the SO line description is correct.
        """
        res = super(SaleOrderLine, self).product_id_change()
        self._onchange_product_id_configurator()
        # product_configurator methods don't take into account this description
        if self.product_id.description_sale:
            self.name = (
                (self.name or '') + '\n' + self.product_id.description_sale
            )
        return res

    def _update_price_configurator(self):
        """If there are enough data (template, pricelist & partner), check new
        price and update line if different.
        """
        self.ensure_one()
        if (not self.product_tmpl_id or not self.order_id.pricelist_id or
                not self.order_id.partner_id):
            return
        product_tmpl = self.product_tmpl_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date_order=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )
        price = self.env['account.tax']._fix_tax_included_price(
            self.price_extra + self._get_display_price(product_tmpl),
            product_tmpl.taxes_id,
            self.tax_id)
        if self.price_unit != price:
            self.price_unit = price

    @api.onchange('product_attribute_ids')
    def _onchange_product_attribute_ids_configurator(self):
        """Update price for having into account possible extra prices"""
        res = super(
            SaleOrderLine, self,
        )._onchange_product_attribute_ids_configurator()
        self._update_price_configurator()
        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        """Update price for having into account changes due to qty"""
        res = super(SaleOrderLine, self).product_uom_change()
        if not self.product_id:
            self._update_price_configurator()
        return res
