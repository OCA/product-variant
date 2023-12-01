# Copyright 2014 AvancOSC - Alfredo de la Fuente
# Copyright 2014 Tecnativa - Pedro M. Baeza
# Copyright 2014 Shine IT - Tony Gu
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2018 Avanzosc S.L. - Daniel Campos
# Copyright 2020 Tecnativa - João Marques
# Copyright 2021 Akretion - Kévin Roche
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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    code_prefix = fields.Char(
        string="Reference Prefix",
        help="Add prefix to product variant reference (default code)",
    )
    reference_mask = fields.Char(
        string="Variant reference mask",
        copy=False,
        store=True,
        compute="_compute_reference_mask",
        inverse="_inverse_reference_mask",
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

    variant_default_code_error = fields.Text(
        compute="_compute_variant_default_code_error"
    )

    def is_automask(self):
        return bool(
            not self.user_has_groups(
                "product_variant_default_code.group_product_default_code_manual_mask"
            )
        )

    @api.depends(
        "code_prefix",
        "attribute_line_ids.value_ids",
        "attribute_line_ids.value_ids.code",
        "attribute_line_ids.value_ids.name",
    )
    def _compute_variant_default_code_error(self):
        automask = self.is_automask()
        for rec in self:
            error_txt = ""
            if not rec.code_prefix and automask:
                error_txt += "Reference Prefix is missing.\n"
            invalid_values = self.attribute_line_ids.value_ids.filtered(
                lambda s: not s.code
            )
            if invalid_values:
                error_txt += (
                    "Following attribute value have an empty code :\n- "
                    + "\n- ".join(invalid_values.mapped("name"))
                )
            if error_txt:
                error_txt = "Default Code can not be computed.\n" + error_txt
            rec.variant_default_code_error = error_txt or False

    @api.depends(
        "code_prefix",
        "attribute_line_ids",
        "attribute_line_ids.attribute_id.name",
    )
    def _compute_reference_mask(self):
        automask = self.is_automask()
        for rec in self:
            if rec.default_code and not rec.code_prefix:
                rec.code_prefix = rec.default_code
            if automask or not rec.reference_mask:
                rec.reference_mask = rec._get_default_mask()
            elif (
                not automask
                and rec.code_prefix
                and rec.code_prefix not in rec.reference_mask
            ):
                rec.reference_mask = rec.code_prefix + rec.reference_mask

    def _inverse_reference_mask(self):
        self._compute_reference_mask()

    def _get_default_mask(self):
        attribute_names = []
        default_reference_separator = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default_reference_separator")
            or ""
        )
        # Get the attribute name in the main lang format, otherwise we could not
        # match mask with the proper values
        main_lang = self._guess_main_lang()
        for line in self.attribute_line_ids:
            attribute_names.append(
                "[{}]".format(line.attribute_id.with_context(lang=main_lang).name)
            )
        default_mask = (self.code_prefix or "") + default_reference_separator.join(
            attribute_names
        )
        return default_mask

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
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
        return super(ProductTemplate, self).create(vals_list)

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

    @api.depends(
        "product_variant_ids", "product_variant_ids.default_code", "code_prefix"
    )
    def _compute_default_code(self):
        super()._compute_default_code()
        if self.env["ir.config_parameter"].get_param("prefix_as_default_code"):
            unique_variants = self.filtered(
                lambda template: len(template.product_variant_ids) == 1
            )
            for template in self - unique_variants:
                template.default_code = template.code_prefix
        return True


class ProductProduct(models.Model):
    _inherit = "product.product"

    manual_code = fields.Boolean(string="Manual Reference", default=False)
    default_code = fields.Char(
        compute="_compute_default_code",
        inverse="_inverse_default_code",
        readonly=False,
        store=True,
    )

    @api.depends(
        "product_tmpl_id.reference_mask",
        "product_template_attribute_value_ids.attribute_id.code",
        "product_template_attribute_value_ids.product_attribute_value_id.code",
    )
    def _compute_default_code(self):
        self.env.cr.flush()  # https://github.com/odoo/odoo/blob/16.0/odoo/models.py#L5592
        for rec in self:
            if not rec.manual_code:
                rec.default_code = rec._generate_default_code()

    def _inverse_default_code(self):
        for rec in self:
            rec.manual_code = bool(rec.default_code)

    def _generate_default_code(self):
        value_codes = self.product_tmpl_id.attribute_line_ids.value_ids.mapped("code")
        if (not self.code_prefix and self.product_tmpl_id.is_automask()) or not all(
            value_codes
        ):
            return None
        else:
            product_attrs = defaultdict(str)
            reference_mask = ReferenceMask(self.product_tmpl_id.reference_mask)
            main_lang = self.product_tmpl_id._guess_main_lang()
            for attr in self.product_template_attribute_value_ids:
                value = attr.product_attribute_value_id
                attr_name = value.attribute_id.with_context(lang=main_lang).name
                if value.attribute_id.code:
                    product_attrs[attr_name] += value.attribute_id.code
                if value.code:
                    product_attrs[attr_name] += value.code
            default_code = reference_mask.safe_substitute(product_attrs)
            return default_code


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    code = fields.Char(
        string="Attribute Code",
    )

    _sql_constraints = [
        ("number_uniq", "unique(name)", _("Attribute Name must be unique!"))
    ]


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code = fields.Char(
        string="Attribute Value Code",
        compute="_compute_code",
        readonly=False,
        store=True,
    )

    @api.depends("code", "name")
    def _compute_code(self):
        for rec in self:
            if rec.name and not rec.code:
                rec.code = rec.name[:2]
