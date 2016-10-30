# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from itertools import chain

from openerp import models, fields, api, exceptions


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _price_rule_get_multi(self, products_qty_partner):

        self.ensure_one()
        date = self._context.get('date', fields.Date.today())
        uom_id = False
        if self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # re browse with uom if given
            products = map(lambda x: x[0], products_qty_partner)
            products_qty_partner = [
                (products[index], data_struct[1], data_struct[2]) for
                index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = categ_ids.keys()

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable(
                            [t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in
                             products]

        # Load all rules
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL '
            '       OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            'ORDER BY item.applied_on, item.min_quantity desc, '
            'categ.parent_left desc',
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to
            # `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a
            # different UoM, in which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = uom_id or product.uom_id.id
            price_uom_id = product.uom_id.id
            price_uom = self.env['product.uom'].browse([qty_uom_id])
            qty_in_product_uom = qty
            if qty_uom_id != price_uom_id:
                try:
                    qty_in_product_uom = price_uom._compute_qty(
                        product.uom_id, qty)
                except exceptions.MissingError:
                    # Ignored - incompatible UoM in context,
                    # use default product UoM
                    pass

            price = self.env['product.template']._price_get(
                [product], 'list_price')[product.id]
            for rule in items:
                if rule.min_quantity and \
                   qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and \
                       product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (
                            product.product_variant_count == 1 and
                            product.product_variant_id.id ==
                            rule.product_id.id):
                        # product rule acceptable on template if
                        # has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and \
                       product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._price_get_multi(
                        [(product, qty, partner)])[product.id]
                    price = rule.base_pricelist_id.currency_id.compute(
                        price_tmp, self.currency_id, round=False)

                else:
                    price = self.env['product.template']._price_get(
                        [product], rule.base)[product.id]
                convert_to_price_uom = (
                    lambda price:
                        product.uom_id._compute_price(price_uom, price)
                )

                if price is not False:
                    if self._context.get('price_extra'):
                        price += self._context.get('price_extra')
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (
                            price * (rule.percent_price / 100))) or 0.0
                    else:
                        price_limit = price
                        price = (price - (
                            price * (rule.percent_price / 100))) or 0.0
                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(
                                rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(
                                rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(
                                rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)

                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and \
               suitable_rule.base != 'pricelist':
                price = product.currency_id.compute(
                    price, self.currency_id, round=False)

            results[product.id] = (
                price, suitable_rule and suitable_rule.id or False)
        return results

    @api.multi
    def price_rule_get_multi(self, products_by_qty_by_partner):

        results = {}
        for pricelist in self:
            subres = pricelist._price_rule_get_multi(
                products_by_qty_by_partner)
            for product_id, price in subres.items():
                results.setdefault(product_id, {})
                results[product_id][pricelist.id] = price
        return results

    @api.multi
    def template_price_get(self, prod_id, qty, partner=None):
        return dict((key, price[0]) for key, price in
                    self.template_price_rule_get(prod_id, qty,
                                                 partner=partner).items())

    @api.model
    def _price_get_multi(self, pricelist, products_by_qty_by_partner):
        return dict(
            (key, price[0]) for key, price in
            pricelist._price_rule_get_multi(products_by_qty_by_partner).items()
        )

    @api.multi
    def template_price_rule_get(self, prod_id, qty, partner=None):
        product = self.env['product.template'].browse(prod_id)
        res_multi = self.price_rule_get_multi(
            products_by_qty_by_partner=[(product, qty, partner)])
        res = res_multi[prod_id]
        return res
