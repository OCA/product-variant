# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import Command
from odoo.tests import Form, TransactionCase


class ProductVariantChangeTemplateCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("product.group_product_variant")
        cls.color = cls._create_attribute("Color", ["Red", "Blue", "Green", "White"])
        cls.size = cls._create_attribute("Size", ["M", "L", "XL"])
        cls.material = cls._create_attribute("Material", ["Cotton", "Silk"])
        cls.engraving = cls._create_attribute(
            "Engraving", ["Yes", "No"], create_variant="no_variant"
        )
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Pricelist"})

    @classmethod
    def _create_attribute(cls, name, values, create_variant="always"):
        # Demo data already has attributes with these names and some modules
        # (e.g. product_variant_default_code) make attribute names unique.
        return cls.env["product.attribute"].create(
            {
                "name": f"{name} (template change test)",
                "create_variant": create_variant,
                "value_ids": [Command.create({"name": v}) for v in values],
            }
        )

    @classmethod
    def _value(cls, attribute, name):
        return attribute.value_ids.filtered(lambda v: v.name == name)

    @classmethod
    def _create_template(cls, name, lines=None, **vals):
        lines = lines or {}
        return cls.env["product.template"].create(
            dict(
                vals,
                name=name,
                attribute_line_ids=[
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [
                                Command.set(
                                    [cls._value(attribute, v).id for v in values]
                                )
                            ],
                        }
                    )
                    for attribute, values in lines.items()
                ],
            )
        )

    def _variant(self, template, *value_names):
        return template.product_variant_ids.filtered(
            lambda p: set(
                p.product_template_attribute_value_ids.product_attribute_value_id.mapped(
                    "name"
                )
            )
            == set(value_names)
        )

    def _open_wizard(self, records):
        return Form(
            self.env["product.variant.change.template"].with_context(
                active_model=records._name, active_ids=records.ids
            )
        )

    def _combination_names(self, variant):
        return set(
            variant.product_template_attribute_value_ids.product_attribute_value_id.mapped(
                "name"
            )
        )

    def _set_line_values(self, wizard_form, index, attribute_values):
        with wizard_form.line_ids.edit(index) as line:
            line.value_ids.clear()
            for attribute, name in attribute_values:
                line.value_ids.add(self._value(attribute, name))
