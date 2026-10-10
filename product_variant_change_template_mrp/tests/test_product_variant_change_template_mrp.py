# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.product_variant_change_template.tests.common import (
    ProductVariantChangeTemplateCommon,
)


@tagged("post_install", "-at_install")
class TestProductVariantChangeTemplateMrp(ProductVariantChangeTemplateCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"]
        cls.leg = product.create({"name": "Leg"})
        cls.red_paint = product.create({"name": "Red paint"})
        cls.blue_paint = product.create({"name": "Blue paint"})
        cls.engraving_kit = product.create({"name": "Engraving kit"})

    def _template_value(self, template, name):
        return template.attribute_line_ids.product_template_value_ids.filtered(
            lambda v: v.name == name
        )

    def _create_bom(self, template, extra_lines=None):
        lines = [
            Command.create({"product_id": self.leg.id, "product_qty": 4}),
            Command.create(
                {
                    "product_id": self.red_paint.id,
                    "bom_product_template_attribute_value_ids": [
                        Command.set(self._template_value(template, "Red").ids)
                    ],
                }
            ),
            Command.create(
                {
                    "product_id": self.blue_paint.id,
                    "bom_product_template_attribute_value_ids": [
                        Command.set(self._template_value(template, "Blue").ids)
                    ],
                }
            ),
        ]
        return self.env["mrp.bom"].create(
            {
                "product_tmpl_id": template.id,
                "bom_line_ids": lines + (extra_lines or []),
            }
        )

    def _find_bom(self, variant):
        return self.env["mrp.bom"]._bom_find(variant)[variant]

    def test_emptied_source_bom_is_narrowed(self):
        target = self._create_template("Table", {self.color: ["Green"]})
        source = self._create_template("Old table", {self.color: ["Red", "Blue"]})
        bom = self._create_bom(source)
        red, blue = self._variant(source, "Red"), self._variant(source, "Blue")
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        self.assertFalse(bom.active)
        for variant, paint in ((red, self.red_paint), (blue, self.blue_paint)):
            variant_bom = self._find_bom(variant)
            self.assertEqual(variant_bom.product_id, variant)
            self.assertEqual(variant_bom.product_tmpl_id, target)
            self.assertEqual(variant_bom.bom_line_ids.product_id, self.leg | paint)
            self.assertFalse(
                variant_bom.bom_line_ids.bom_product_template_attribute_value_ids
            )
        self.assertFalse(self._find_bom(self._variant(target, "Green")))

    def test_partial_move_replaces_source_bom(self):
        target = self._create_template("Table", {self.color: ["Green"]})
        source = self._create_template("Old table", {self.color: ["Red", "Blue"]})
        bom = self._create_bom(source)
        red, blue = self._variant(source, "Red"), self._variant(source, "Blue")
        wizard_form = self._open_wizard(blue)
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        self.assertFalse(bom.active)
        source_bom = self._find_bom(red)
        self.assertEqual(source_bom.product_tmpl_id, source)
        self.assertFalse(source_bom.product_id)
        self.assertEqual(
            source_bom.bom_line_ids.product_id,
            self.leg | self.red_paint,
            "The blue paint line must not start applying to every variant",
        )
        blue_bom = self._find_bom(blue)
        self.assertEqual(blue_bom.product_id, blue)
        self.assertEqual(blue_bom.bom_line_ids.product_id, self.leg | self.blue_paint)

    def test_non_variant_restriction_is_refused(self):
        target = self._create_template("Table", {self.color: ["Green"]})
        source = self._create_template(
            "Old table", {self.color: ["Red", "Blue"], self.engraving: ["Yes", "No"]}
        )
        bom = self._create_bom(
            source,
            [
                Command.create(
                    {
                        "product_id": self.engraving_kit.id,
                        "bom_product_template_attribute_value_ids": [
                            Command.set(self._template_value(source, "Yes").ids)
                        ],
                    }
                )
            ],
        )
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard = wizard_form.save()
        with self.assertRaisesRegex(UserError, "do not create variants"):
            wizard.action_move()
        self.assertTrue(bom.active)
        self.assertEqual(source.product_variant_ids.product_tmpl_id, source)
