# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from openerp import api, fields, models, exceptions, _
from openerp.addons import decimal_precision as dp


class ProductConfigurator(models.AbstractModel):
    _name = 'product.configurator'

    product_tmpl_id = fields.Many2one(
        string='Product Template',
        comodel_name='product.template',
        auto_join=True)
    product_attribute_ids = fields.One2many(
        comodel_name='product.configurator.attribute',
        domain=lambda self: [("owner_model", "=", self._name)],
        inverse_name='owner_id',
        string='Product attributes',
        copy=True)
    price_extra = fields.Float(
        compute='_compute_price_extra',
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with the currently "
             "selected attributes values on sale price. eg. 200 price extra, "
             "1000 + 200 = 1200.")
    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product")
    name = fields.Char()

    @api.depends('product_attribute_ids', 'product_attribute_ids.value_id')
    def _compute_price_extra(self):
        for record in self:
            record.price_extra = sum(
                record.mapped('product_attribute_ids.price_extra'))

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if not self.product_tmpl_id:
            return {}

        # First, empty current list
        attribute_lines = self.product_attribute_ids.browse([])
        if not self.product_tmpl_id.attribute_line_ids:
            self.product_id = \
                self.product_tmpl_id.product_variant_ids[0].id
        else:
            if not self.env.context.get('not_reset_product'):
                self.product_id = False

            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                attribute_lines += attribute_lines.new({
                    'attribute_id': attribute_line.attribute_id.id,
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'owner_model': self._name,
                    'owner_id': self.id,
                })
        self.product_attribute_ids = attribute_lines

        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}

    @api.onchange('product_attribute_ids')
    def onchange_product_attribute_ids(self):
        if not self.product_attribute_ids:
            return {}
        product_obj = self.env['product.product']
        domain, cont = product_obj._build_attributes_domain(
            self.product_tmpl_id, self.product_attribute_ids)
        self.product_id = False
        if cont:
            products = product_obj.search(domain)
            # Filter the product with the exact number of attributes values
            for product in products:
                if len(product.attribute_value_ids) == cont:
                    self.product_id = product.id
                    break
        if not self.product_id:
            product_tmpl = self.product_tmpl_id
            values = self.product_attribute_ids.mapped('value_id')
            if 'partner_id' in self._fields:
                # If our model has a partner_id field, language is got from it
                obj = self.env['product.attribute.value'].with_context(
                    lang=self.partner_id.lang)
                values = obj.browse(
                    self.product_attribute_ids.mapped('value_id').ids)
                obj = self.env['product.template'].with_context(
                    lang=self.partner_id.lang)
                product_tmpl = obj.browse(self.product_tmpl_id.id)
            self.name = self._get_product_description(
                product_tmpl, False, values)
        return {'domain': {'product_id': domain}}

    @api.multi
    def onchange_product_id_product_configurator(self):
        # First, empty current list

        self.ensure_one()
        if self.product_id:
            self.product_attribute_ids = [
                (2, x.id) for x in self.product_attribute_ids]
            attribute_list = (
                self.product_id._get_product_attributes_values_dict())
            for val in attribute_list:
                val['product_tmpl_id'] = self.product_id.product_tmpl_id
                val['owner_model'] = self._name
            product = self.product_id
            if 'partner_id' in self._fields:
                # If our model has a partner_id field, language is got from it
                product = self.env['product.product'].with_context(
                    lang=self.partner_id.lang).browse(self.product_id.id)
            self.product_attribute_ids = [(0, 0, x) for x in attribute_list]
            self.product_tmpl_id = product.product_tmpl_id.id
            self.name = self._get_product_description(
                product.product_tmpl_id, product, product.attribute_value_ids)

    @api.multi
    def onchange_product_id_product_configurator_old_api(
            self, product_id, partner_id=None):
        """Method to be called in case inherited model use old API on_change.

        The returned result has to be merged with current 'value' key in the
        regular on_change method, not with the complete dictionary.

        :param product_id: ID of the changed product.
        :param partner_id: ID of the partner in the model.
        :return: Dictionary with the changed values.
        """
        res = {}
        if product_id:
            product_obj = self.env['product.product']
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                product_obj = product_obj.with_context(lang=partner.lang)
            product = product_obj.browse(product_id)
            attr_values_dict = product._get_product_attributes_values_dict()
            for val in attr_values_dict:
                val['product_tmpl_id'] = product.product_tmpl_id.id
                val['owner_model'] = self._name
                val['owner_id'] = self.id
            attr_values = [(0, 0, values) for values in attr_values_dict]
            res['product_attribute_ids'] = attr_values
            res['product_tmpl_id'] = product.product_tmpl_id.id
            res['name'] = self._get_product_description(
                product.product_tmpl_id, product,
                product.attribute_value_ids)
        return res

    @api.model
    def _order_attributes(self, template, product_attribute_values):
        res = template._get_product_attributes_dict()
        res2 = []
        for val in res:
            value = product_attribute_values.filtered(
                lambda x: x.attribute_id.id == val['attribute_id'])
            if value:
                val['value_id'] = value
                res2.append(val)
        return res2

    @api.model
    def _get_product_description(self, template, product, product_attributes):
        name = product and product.name or template.name
        extended = self.user_has_groups(
            'product_variant_configurator.'
            'group_product_variant_extended_description')
        if not product_attributes and product:
            product_attributes = product.attribute_value_ids
        values = self._order_attributes(template, product_attributes)
        if extended:
            description = "\n".join(
                "%s: %s" %
                (x['value_id'].attribute_id.name, x['value_id'].name)
                for x in values)
        else:
            description = ", ".join([x['value_id'].name for x in values])
        if not description:
            return name
        return ("%s\n%s" if extended else "%s (%s)") % (name, description)

    @api.multi
    def unlink(self):
        """Mimic `ondelete="cascade"`."""
        attributes = self.mapped("product_attribute_ids")
        result = super(ProductConfigurator, self).unlink()
        if result:
            attributes.unlink()
        return result

    @api.model
    def check_configuration_validity(self, vals):
        """The method checks that the current selection values are correct.

        As default, the validity means that all the attributes
        values are set. This can be overridden to set another rules.

        :param vals: Dictionary of values that creates the record
        :type vals: dict
        :raises: exceptions.ValidationError: If the check is not valid.
        """
        if any(not x[2].get('value_id') for
               x in vals.get('product_attribute_ids', [])):
            raise exceptions.ValidationError(
                _("You have to fill all the attributes values."))

    @api.multi
    def _create_variant_from_vals(self, vals):
        """The method creates a product variant extracting the needed values.

        the values dictionary is provided from the ORM methods create/write.
        It also takes the rest of the values from the associated recordset
        in self if needed, or raise an ensure_one exception if not provided.
        :param vals: Dictionary of values for the record creation/update.
        :return: The same values dictionary with the ID of the created product
        in it under the key `product_id`.
        """
        attribute_obj = self.env['product.configurator.attribute']
        product_attributes_dict = vals.get('product_attribute_ids')
        if not vals.get('product_attribute_ids'):
            self.ensure_one()
            product_attributes_dict = self._convert_to_write(self._cache)
        product_tmpl_id = vals.get('product_tmpl_id', self.product_tmpl_id.id)
        value_ids = []
        for op in product_attributes_dict:
            if op[0] == 4:
                attribute = attribute_obj.browse(op[1])
                if attribute.value_id:
                    value_ids.append(attribute.value_id.id)
            elif op[0] in (0, 1):
                if 'value_id' in op[2]:
                    if op[2]['value_id']:
                        value_ids.append(op[2]['value_id'])
                else:
                    attribute = attribute_obj.browse(op[1])
                    if attribute.value_id:
                        value_ids.append(attribute.value_id.id)
            elif op[0] == 6:
                value_ids = []
                attribute_values = attribute_obj.browse(op[2]).mapped(
                    'value_id')
                value_ids.extend(attribute_values.ids)
        product = self.env['product.product'].create({
            'product_tmpl_id': product_tmpl_id,
            'attribute_value_ids': [(6, 0, value_ids)],
        })
        vals['product_id'] = product.id
        return vals
