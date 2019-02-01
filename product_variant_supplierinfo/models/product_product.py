# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    seller_ids = fields.Many2many(
        'product.supplierinfo',
        compute='compute_seller_ids',
        store=True)
    seller_delay = fields.Integer(
        related='seller_ids.delay',
        string='Supplier Lead Time',
        help=("This is the average delay in days between the purchase order "
              "confirmation and the receipts for this product and for the "
              "default supplier. It is used by the scheduler to order "
              "requests based on reordering delays."))
    seller_qty = fields.Float(
        related='seller_ids.min_qty',
        string='Supplier Min Quantity',
        help="This is minimum quantity to purchase from Main Supplier.")
    seller_id = fields.Many2one(
        related='seller_ids.name',
        relation='res.partner',
        string='Main Supplier',
        help="Main Supplier who has highest priority in Supplier List.")
    variant_seller_ids = fields.One2many(
        'product.supplierinfo',
        'product_id')
    tmpl_seller_ids = fields.Many2many(
        'product.supplierinfo',
        compute='compute_seller_ids',
        store=True,)

    @api.multi
    @api.depends('product_tmpl_id.seller_ids.product_id')
    def compute_seller_ids(self):
        for product in self:
            sellers = product.product_tmpl_id.seller_ids
            product.tmpl_seller_ids = sellers
            product.seller_ids = sellers.filtered(lambda x: x.product_id == product)
