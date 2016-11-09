# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# © 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

import logging
from openerp import api, fields, models, exceptions, _
from openerp.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductConfigurator(models.AbstractModel):
    _name = 'product.configurator'

    product_tmpl_id = fields.Many2one(
        string='Product Template',
        comodel_name='product.template',
        auto_join=True)
    product_attribute_ids = fields.One2many(
        comodel_name='product.configurator.attribute',
        domain=lambda self: [("owner_model", "=", self._name)],
        inverse_name='owner_id', string='Product attributes', copy=True)
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
    can_create_product = fields.Boolean(
        compute='_compute_can_be_created',
        store=False)
    create_product_variant = fields.Boolean(
        string="Create product now!")

    @api.depends('product_attribute_ids', 'product_attribute_ids.value_id',
                 'product_id')
    def _compute_can_be_created(self):
        if self.product_id:
            # product already selected
            self.can_create_product = False
            return
        if not self.product_tmpl_id:
            # no product nor template
            self.can_create_product = False
            return
        self.can_create_product = not bool(
            len(self.product_tmpl_id.attribute_line_ids.mapped('attribute_id')) -
            len(filter(None, self.product_attribute_ids.mapped('value_id'))))

    @api.depends('product_attribute_ids', 'product_attribute_ids.value_id')
    def _compute_price_extra(self):
        for record in self:
            record.price_extra = sum(
                record.mapped('product_attribute_ids.price_extra'))

    def _set_product_tmpl_attributes(self):
        if self.product_tmpl_id:
            attribute_lines = self.product_attribute_ids.browse([])
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                attribute_lines += attribute_lines.new({
                    'attribute_id': attribute_line.attribute_id.id,
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'owner_model': self._name,
                    'owner_id': self.id,
                })
            self.product_attribute_ids = attribute_lines

    def _set_product_attributes(self):
        if self.product_id:
            attribute_lines = self.product_attribute_ids.browse([])
            for vals in self.product_id._get_product_attributes_values_dict():
                vals['product_tmpl_id'] = self.product_id.product_tmpl_id
                vals['owner_model'] = self._name
                vals['owner_id'] = self.id
                attribute_lines += attribute_lines.new(vals)
            self.product_attribute_ids = attribute_lines

    def _empty_attributes(self):
        self.product_attribute_ids = self.product_attribute_ids.browse([])

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id_configurator(self):
        if not self.product_tmpl_id:
            self.product_id = False
            self._empty_attributes()
            # no product template: allow any product
            return {'domain': {'product_id': []}}

        if not self.product_tmpl_id.attribute_line_ids:
            # template without attribute, use the unique variant
            self.product_id = \
                self.product_tmpl_id.product_variant_ids[0].id
        else:
            # verify the product correspond to the template
            # otherwise reset it
            if (self.product_id and
                    self.product_id.product_tmpl_id != self.product_tmpl_id):
                if not self.env.context.get('not_reset_product'):
                    self.product_id = False

        # populate attributes
        if self.product_id:
            self._set_product_attributes()
        elif self.product_tmpl_id:
            self._set_product_tmpl_attributes()
        else:
            self._empty_attributes()

        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}

    @api.onchange('product_attribute_ids')
    def onchange_product_attribute_ids(self):
        if not self.product_tmpl_id:
            return {'domain': {'product_id': []}}
        if not self.product_attribute_ids:
            domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
            return {'domain': {'product_id': domain}}
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

    @api.onchange('product_id')
    def onchange_product_id_configurator(self):
        if self.product_id:
            product = self.product_id
            if 'partner_id' in self._fields:
                # If our model has a partner_id field, language is got from it
                product = self.env['product.product'].with_context(
                    lang=self.partner_id.lang).browse(self.product_id.id)
            self.name = self._get_product_description(
                product.product_tmpl_id, product, product.attribute_value_ids)
            self.product_tmpl_id = product.product_tmpl_id.id
            self._set_product_attributes()
        elif self.product_tmpl_id:
            self._set_product_tmpl_attributes()
        else:
            self._empty_attributes()

    @api.onchange('create_product_variant')
    def onchange_create_product_variant(self):
        if not self.create_product_variant:
            return
        self.create_product_variant = False
        try:
            with self.env.cr.savepoint():
                self.product_id = self.create_variant_if_needed()
        except exceptions.ValidationError as e:
            _logger.exception('Product not created!')
            return {'warning': {
                'title': _('Product not created!'),
                'message': e.name,
            }}

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

    @api.multi
    def create_variant_if_needed(self):
        """ Create the product variant

        Check if the configuration if valid by calling
        check_configuration_validity. The search for an existing
        product with the selected attributes. If not found, create
        a new product.

        :returns: the product (found our newly created)
        """
        self.ensure_one()
        # TODO: search for existing product matching the attribute values
        values = self.product_attribute_ids.mapped('value_id.id')
        return self.env['product.product'].create({
            'product_tmpl_id': self.product_tmpl_id.id,
            'attribute_value_ids': [(4, value) for value in values]
        })

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
