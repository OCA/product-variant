# Copyright 2014 AvancOSC - Alfredo de la Fuente
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2014 Shine IT - Tony Gu
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Avanzosc S.L. - Daniel Campos
# Copyright 2020 Tecnativa - João Marques
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from collections import defaultdict
from string import Template

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReferenceMask(Template):
    pattern = r"""\[(?:
                    (?P<escaped>\[) |
                    (?P<named>[^\]]+?)\] |
                    (?P<braced>[^\]]+?)\] |
                    (?P<invalid>)
                    )"""


def extract_token(s):
    pattern = re.compile(r"\[([^\]]+?)\]")
    return set(pattern.findall(s))


def sanitize_reference_mask(product, mask):
    main_lang = product._guess_main_lang()
    tokens = extract_token(mask)
    attribute_names = set()
    for line in product.attribute_line_ids:
        attribute_names.add(line.attribute_id.with_context(lang=main_lang).name)
    if not tokens.issubset(attribute_names):
        raise UserError(
            _('Found unrecognized attribute name in "Variant ' 'Reference Mask"')
        )


def get_rendered_default_code(product, mask):
    product_attrs = defaultdict(str)
    reference_mask = ReferenceMask(mask)
    main_lang = product.product_tmpl_id._guess_main_lang()
    for attr in product.product_template_attribute_value_ids:
        value = attr.product_attribute_value_id
        attr_name = value.attribute_id.with_context(lang=main_lang).name
        if value.attribute_id.code:
            product_attrs[attr_name] += value.attribute_id.code
        if value.code:
            product_attrs[attr_name] += value.code
    all_attrs = extract_token(mask)
    missing_attrs = all_attrs - set(product_attrs.keys())
    missing = dict.fromkeys(
        missing_attrs,
        product.env["ir.config_parameter"]
        .sudo()
        .get_param("default_reference_missing_placeholder"),
    )
    product_attrs.update(missing)
    default_code = reference_mask.safe_substitute(product_attrs)
    return default_code


def render_default_code(product, mask):
    product.default_code = get_rendered_default_code(product, mask)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    code_prefix = fields.Char(
        string="Reference Prefix",
        help="Add prefix to product variant reference (default code)",
    )
    reference_mask = fields.Char(
        string="Variant reference mask",
        copy=False,
        help="Reference mask for building internal references of a "
        "variant generated from this template.\n"
        "Example:\n"
        "A product named ABC with 2 attributes: Size and Color:\n"
        "Product: ABC\n"
        "Color: Red(r), Yellow(y), Black(b)  #Red, Yellow, Black are "
        "the attribute value, `r`, `y`, `b` are the corresponding code\n"
        "Size: L (l), XL(x)\n"
        "When setting Variant reference mask to `[Color]-[Size]`, the "
        "default code on the variants will be something like `r-l` "
        "`b-l` `r-x` ...\n"
        "If you like, You can even have the attribute name appear more"
        " than once in the mask. Such as,"
        "`fancyA/[Size]~[Color]~[Size]`\n"
        " When saved, the default code on variants will be "
        "something like \n"
        ' `fancyA/l~r~l` (for variant with Color "Red" and Size "L") '
        ' `fancyA/x~y~x` (for variant with Color "Yellow" and Size "XL")'
        '\nNote: make sure characters "[,]" do not appear in your '
        "attribute name",
    )

    def _get_default_mask(self):
        attribute_names = []
        default_reference_separator = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default_reference_separator")
        )
        # Get the attribute name in the main lang format, otherwise we could not
        # match mask with the proper values
        main_lang = self._guess_main_lang()
        for line in self.attribute_line_ids:
            attribute_names.append(
                u"[{}]".format(line.attribute_id.with_context(lang=main_lang).name)
            )
        default_mask = (self.code_prefix or "") + default_reference_separator.join(
            attribute_names
        )
        return default_mask

    @api.model
    def create(self, vals):
        product = self.new(vals)
        if (
            not vals.get("reference_mask")
            and product.attribute_line_ids
            or not self.user_has_groups(
                "product_variant_default_code.group_product_default_code_manual_mask"
            )
        ):
            vals["reference_mask"] = product._get_default_mask()
        elif vals.get("reference_mask"):
            sanitize_reference_mask(product, vals["reference_mask"])
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        with_variants = self.env["product.template"]
        product_obj = self.env["product.product"]
        if (
            "reference_mask" in vals
            and not vals["reference_mask"]
            or not self.user_has_groups(
                "product_variant_default_code.group_product_default_code_manual_mask"
            )
        ):
            with_variants = self.filtered("attribute_line_ids")
            for template in with_variants:
                new_dict = dict(vals)
                new_dict["reference_mask"] = template._get_default_mask()
                super(ProductTemplate, template).write(new_dict)
        super(ProductTemplate, self - with_variants).write(vals)
        if vals.get("reference_mask"):
            cond = [("product_tmpl_id", "=", self.id), ("manual_code", "=", False)]
            products = product_obj.search(cond)
            for product in products:
                if product.reference_mask:
                    render_default_code(product, product.reference_mask)
        return True

    @api.model
    def _guess_main_lang(self):
        """Used by get_rendered_default_code()"""
        english = self.env.ref("base.lang_en")
        if english.active:
            return english.code
        else:
            # Naive/simple implementation:
            # you may inherit to override it in your custom code
            # to return the language code of your choice
            return self.env["res.lang"].search([], limit=1).code


class ProductProduct(models.Model):
    _inherit = "product.product"

    manual_code = fields.Boolean(string="Manual Reference")

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        if product.reference_mask:
            render_default_code(product, product.reference_mask)
        return product

    @api.onchange("default_code")
    def onchange_default_code(self):
        self.manual_code = bool(self.default_code)


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char(
        string="Attribute Code",
    )

    _sql_constraints = [
        ("number_uniq", "unique(name)", _("Attribute Name must be unique!"))
    ]

    def write(self, vals):
        if "code" not in vals:
            return super(ProductAttribute, self).write(vals)
        result = super(ProductAttribute, self).write(vals)
        # Rewrite reference on all product variants affected
        for product in self.mapped(
            "attribute_line_ids.product_tmpl_id.product_variant_ids"
        ).filtered(lambda x: x.product_tmpl_id.reference_mask and not x.manual_code):
            render_default_code(product, product.reference_mask)
        return result


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.onchange("name")
    def onchange_name(self):
        """Set a default code for the value"""
        if self.name and not self.code:
            self.code = self.name[:2]

    code = fields.Char(
        string="Attribute Value Code",
        default=onchange_name,
    )

    @api.model
    def create(self, vals):
        if "code" not in vals:
            vals["code"] = vals.get("name", "")[0:2]
        return super(ProductAttributeValue, self).create(vals)

    def write(self, vals):
        if "code" not in vals:
            return super(ProductAttributeValue, self).write(vals)
        result = super(ProductAttributeValue, self).write(vals)
        # Rewrite reference on all product variants affected
        for product in (
            self.env["product.product"]
            .search(
                [
                    (
                        "product_template_attribute_value_ids"
                        ".product_attribute_value_id",
                        "in",
                        self.ids,
                    )
                ]
            )
            .filtered(lambda x: x.product_tmpl_id.reference_mask and not x.manual_code)
            .mapped("product_tmpl_id.product_variant_ids")
        ):
            render_default_code(product, product.reference_mask)
        return result
