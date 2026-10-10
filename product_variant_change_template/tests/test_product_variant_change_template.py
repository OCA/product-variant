# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests import tagged

from .common import ProductVariantChangeTemplateCommon


@tagged("post_install", "-at_install")
class TestProductVariantChangeTemplate(ProductVariantChangeTemplateCommon):
    def _add_value_from_template_form(self, template, attribute, name):
        """Save the template form after adding a value to an attribute line.

        The form onchange is skipped: with exclusions on the template, some
        modules (e.g. product_variant_configurator_manual_creation) make the
        core search exclusions by the id of the unsaved record, which only
        logs a warning, unrelated to this module."""
        line = template.attribute_line_ids.filtered(
            lambda ln: ln.attribute_id == attribute
        )
        template.write(
            {
                "attribute_line_ids": [
                    Command.update(
                        line.id,
                        {"value_ids": [Command.link(self._value(attribute, name).id)]},
                    )
                ]
            }
        )

    def test_move_simple_products(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        shirt_m = target.product_variant_ids
        source_l = self._create_template("Shirt L", default_code="SHIRT-L")
        source_xl = self._create_template("Shirt XL")
        variant_l = source_l.product_variant_ids
        variant_xl = source_xl.product_variant_ids
        vendor_price = self.env["product.supplierinfo"].create(
            {"partner_id": self.vendor.id, "product_tmpl_id": source_l.id, "price": 7}
        )
        rule = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": source_xl.id,
                "fixed_price": 11,
            }
        )
        wizard_form = self._open_wizard(source_l | source_xl)
        wizard_form.target_tmpl_id = target
        # The only size of the target is proposed, which clashes with Shirt M
        self.assertTrue(wizard_form.has_errors)
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        self._set_line_values(wizard_form, 1, [(self.size, "XL")])
        self.assertFalse(wizard_form.has_errors)
        wizard_form.save().action_move()
        self.assertEqual(target.product_variant_ids, shirt_m | variant_l | variant_xl)
        self.assertEqual(variant_l.product_tmpl_id, target)
        self.assertEqual(variant_l.default_code, "SHIRT-L")
        self.assertEqual(self._combination_names(variant_xl), {"XL"})
        self.assertEqual(
            set(target.attribute_line_ids.value_ids.mapped("name")), {"M", "L", "XL"}
        )
        self.assertFalse(source_l.active)
        self.assertFalse(source_xl.active)
        self.assertEqual(vendor_price.product_tmpl_id, target)
        self.assertEqual(vendor_price.product_id, variant_l)
        self.assertEqual(rule.applied_on, "0_product_variant")
        self.assertEqual(rule.product_id, variant_xl)
        self.assertEqual(rule.product_tmpl_id, target)

    def test_missing_combination_excluded(self):
        target = self._create_template(
            "Shirt", {self.color: ["Red", "Blue"], self.size: ["M", "L"]}
        )
        source = self._create_template("Shirt Red XL")
        variant = source.product_variant_ids
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        self._set_line_values(wizard_form, 0, [(self.color, "Red"), (self.size, "XL")])
        wizard_form.save().action_move()
        self.assertEqual(len(target.product_variant_ids), 5)
        self.assertEqual(self._combination_names(variant), {"Red", "XL"})
        exclusion = self.env["product.template.attribute.exclusion"].search(
            [("product_tmpl_id", "=", target.id)]
        )
        self.assertEqual(len(exclusion), 1)
        self.assertEqual(
            {exclusion.product_template_attribute_value_id.name}
            | set(exclusion.value_ids.mapped("name")),
            {"Blue", "XL"},
        )
        # A later change of the attributes keeps the moved variant and does not
        # bring the excluded combination back
        self._add_value_from_template_form(target, self.color, "Green")
        self.assertTrue(variant.active)
        self.assertEqual(variant.product_tmpl_id, target)
        self.assertTrue(self._variant(target, "Green", "XL"))
        self.assertFalse(self._variant(target, "Blue", "XL"))
        self.assertEqual(len(target.product_variant_ids), 8)

    def test_missing_combination_created(self):
        target = self._create_template(
            "Shirt", {self.color: ["Red", "Blue"], self.size: ["M", "L"]}
        )
        source = self._create_template("Shirt Red XL")
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.missing_combination_policy = "create"
        self._set_line_values(wizard_form, 0, [(self.color, "Red"), (self.size, "XL")])
        wizard_form.save().action_move()
        self.assertEqual(len(target.product_variant_ids), 6)
        self.assertTrue(self._variant(target, "Blue", "XL"))
        self.assertFalse(
            self.env["product.template.attribute.exclusion"].search(
                [("product_tmpl_id", "=", target.id)]
            )
        )

    def test_new_attribute_for_existing_variants(self):
        target = self._create_template("Pants", {self.color: ["Red", "Blue"]})
        red, blue = self._variant(target, "Red"), self._variant(target, "Blue")
        source = self._create_template(
            "Silk pants", {self.color: ["Red", "Green"], self.material: ["Silk"]}
        )
        moved = source.product_variant_ids
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        self.assertTrue(wizard_form.has_errors)
        with wizard_form.attribute_default_ids.edit(0) as default:
            self.assertEqual(default.attribute_id, self.material)
            default.value_id = self._value(self.material, "Cotton")
        wizard_form.save().action_move()
        self.assertEqual(target.product_variant_ids, red | blue | moved)
        self.assertEqual(self._combination_names(red), {"Red", "Cotton"})
        self.assertEqual(self._combination_names(blue), {"Blue", "Cotton"})
        self.assertEqual(
            {frozenset(self._combination_names(v)) for v in moved},
            {frozenset({"Red", "Silk"}), frozenset({"Green", "Silk"})},
        )
        self.assertFalse(source.active)
        self._add_value_from_template_form(target, self.color, "White")
        self.assertEqual(
            len(target.product_variant_ids), 6, "Only White variants are added"
        )
        self.assertTrue((red | blue | moved).exists())
        self.assertFalse(self._variant(target, "Green", "Cotton"))
        self.assertFalse(self._variant(target, "Blue", "Silk"))

    def test_partial_move_keeps_source_consistent(self):
        source = self._create_template(
            "Shirt", {self.color: ["Red", "Blue"], self.size: ["M", "L"]}
        )
        target = self._create_template(
            "Premium shirt", {self.color: ["Red"], self.size: ["XL"]}
        )
        moved = self._variant(source, "Blue", "L")
        remaining = source.product_variant_ids - moved
        wizard_form = self._open_wizard(moved)
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        self.assertTrue(source.active)
        self.assertEqual(source.product_variant_ids, remaining)
        self.assertEqual(len(target.product_variant_ids), 2)
        self.assertEqual(moved.product_tmpl_id, target)
        self._add_value_from_template_form(source, self.size, "XL")
        self.assertTrue(remaining.exists())
        self.assertFalse(self._variant(source, "Blue", "L"))
        self.assertEqual(len(source.product_variant_ids), 5)

    def test_partial_move_removes_unused_values(self):
        source = self._create_template("Shirt", {self.size: ["M", "L"]})
        target = self._create_template("Premium shirt", {self.size: ["XL"]})
        moved = self._variant(source, "L")
        wizard_form = self._open_wizard(moved)
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        self.assertEqual(source.attribute_line_ids.value_ids.mapped("name"), ["M"])
        self.assertEqual(len(source.product_variant_ids), 1)
        self.assertEqual(
            set(target.attribute_line_ids.value_ids.mapped("name")), {"L", "XL"}
        )

    def test_variants_from_several_templates(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        first = self._create_template("Shirt A", {self.size: ["L", "XL"]})
        second = self._create_template("Shirt B", {self.size: ["L"]})
        first_xl = self._variant(first, "XL")
        second_l = second.product_variant_ids
        wizard_form = self._open_wizard(first_xl | second_l)
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        self.assertEqual((first_xl | second_l).product_tmpl_id, target)
        self.assertTrue(first.active)
        self.assertFalse(second.active)

    def test_incompatible_templates_are_blocked(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        source = self._create_template(
            "Shirt L",
            uom_id=self.env.ref("uom.product_uom_dozen").id,
            uom_po_id=self.env.ref("uom.product_uom_dozen").id,
        )
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        self.assertTrue(wizard_form.has_errors)
        wizard = wizard_form.save()
        with self.assertRaises(UserError):
            wizard.action_move()
        self.assertEqual(source.product_variant_ids.product_tmpl_id, source)

    def test_existing_exclusion_is_respected(self):
        target = self._create_template(
            "Shirt", {self.color: ["Red", "Blue"], self.size: ["M", "L"]}
        )
        blue = target.attribute_line_ids[0].product_template_value_ids.filtered(
            lambda v: v.name == "Blue"
        )
        size_l = target.attribute_line_ids[1].product_template_value_ids.filtered(
            lambda v: v.name == "L"
        )
        self.env["product.template.attribute.exclusion"].create(
            {
                "product_tmpl_id": target.id,
                "product_template_attribute_value_id": blue.id,
                "value_ids": [Command.set(size_l.ids)],
            }
        )
        source = self._create_template("Shirt Blue L")
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        self._set_line_values(wizard_form, 0, [(self.color, "Blue"), (self.size, "L")])
        self.assertTrue(wizard_form.has_errors)
        self.assertIn("exclusion", wizard_form.preview)

    def test_no_variant_attributes_are_copied(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        source = self._create_template("Shirt L", {self.engraving: ["Yes"]})
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        self.assertIn(
            f"{self.engraving.name} (does not create variants)", wizard_form.preview
        )
        wizard_form.save().action_move()
        engraving_line = target.attribute_line_ids.filtered(
            lambda ln: ln.attribute_id == self.engraving
        )
        self.assertEqual(engraving_line.value_ids.mapped("name"), ["Yes"])
        self.assertEqual(len(target.product_variant_ids), 2)

    def test_emptied_multi_variant_source_specializes_records(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        source = self._create_template("Shirt big", {self.size: ["L", "XL"]})
        variant_l, variant_xl = self._variant(source, "L"), self._variant(source, "XL")
        vendor_price = self.env["product.supplierinfo"].create(
            {"partner_id": self.vendor.id, "product_tmpl_id": source.id, "price": 5}
        )
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.save().action_move()
        prices = self.env["product.supplierinfo"].search(
            [("partner_id", "=", self.vendor.id)]
        )
        self.assertEqual(len(prices), 2)
        self.assertIn(vendor_price, prices)
        self.assertEqual(prices.product_tmpl_id, target)
        self.assertEqual(prices.product_id, variant_l | variant_xl)
        self.assertEqual(set(prices.mapped("price")), {5})

    def test_merge_source_template(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        source = self._create_template("Shirt L")
        self.env["ir.model.data"].create(
            {
                "module": "__import__",
                "name": "shirt_l",
                "model": "product.template",
                "res_id": source.id,
            }
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": "spec.txt",
                "res_model": "product.template",
                "res_id": source.id,
                "raw": b"spec",
            }
        )
        source.message_post(body="Old note")
        server_action = self.env["ir.actions.server"].create(
            {
                "name": "Use the source template",
                "model_id": self.env["ir.model"]._get_id("product.supplierinfo"),
                "state": "object_write",
                "update_path": "product_tmpl_id",
                "evaluation_type": "value",
                "resource_ref": f"product.template,{source.id}",
            }
        )
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.source_template_policy = "merge"
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        wizard_form.save().action_move()
        self.assertFalse(source.exists())
        self.assertEqual(self.env.ref("__import__.shirt_l"), target)
        self.assertEqual(attachment.res_id, target.id)
        self.assertIn("Old note", "".join(target.message_ids.mapped("body")))
        self.assertEqual(server_action.resource_ref, target)

    def test_merge_falls_back_to_archive(self):
        target = self._create_template("Shirt", {self.size: ["M"]})
        source = self._create_template("Shirt L")
        self.env["ir.model.data"].create(
            {
                "module": "product_variant_change_template",
                "name": "test_shirt_l",
                "model": "product.template",
                "res_id": source.id,
            }
        )
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.source_template_policy = "merge"
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        wizard_form.save().action_move()
        self.assertTrue(source.exists())
        self.assertFalse(source.active)
        self.assertIn("not merged", target.message_ids[0].body)

    def _skip_if_variant_prices_are_independent(self):
        if self.env[
            "product.variant.change.template"
        ]._variant_prices_are_independent():
            self.skipTest("Each variant stores its own price, extras are not used")

    def test_keep_sale_price(self):
        target = self._create_template("Shirt", {self.size: ["M"]}, list_price=10)
        source_l = self._create_template("Shirt L", list_price=12)
        source_xl = self._create_template("Shirt XL", list_price=15)
        wizard_form = self._open_wizard(source_l | source_xl)
        wizard_form.target_tmpl_id = target
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        self._set_line_values(wizard_form, 1, [(self.size, "XL")])
        self.assertNotIn("sales price", wizard_form.preview)
        wizard_form.save().action_move()
        self.assertEqual(self._variant(target, "M").lst_price, 10)
        self.assertEqual(self._variant(target, "L").lst_price, 12)
        self.assertEqual(self._variant(target, "XL").lst_price, 15)

    def test_keep_sale_price_with_new_attribute(self):
        self._value(self.material, "Cotton").default_extra_price = 3
        target = self._create_template(
            "Pants", {self.color: ["Red", "Blue"]}, list_price=10
        )
        red, blue = self._variant(target, "Red"), self._variant(target, "Blue")
        source = self._create_template(
            "Silk pants", {self.color: ["Red"], self.material: ["Silk"]}, list_price=20
        )
        moved = source.product_variant_ids
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        with wizard_form.attribute_default_ids.edit(0) as default:
            default.value_id = self._value(self.material, "Cotton")
        wizard_form.save().action_move()
        self.assertEqual(red.lst_price, 10)
        self.assertEqual(blue.lst_price, 10)
        self.assertEqual(moved.lst_price, 20)

    def test_sale_price_conflict_is_warned(self):
        self._skip_if_variant_prices_are_independent()
        target = self._create_template(
            "Shirt", {self.color: ["Red", "Blue"], self.size: ["M"]}, list_price=10
        )
        red_l = self._create_template("Shirt Red L", list_price=12)
        blue_l = self._create_template("Shirt Blue L", list_price=13)
        wizard_form = self._open_wizard(red_l | blue_l)
        wizard_form.target_tmpl_id = target
        self._set_line_values(wizard_form, 0, [(self.color, "Red"), (self.size, "L")])
        self._set_line_values(wizard_form, 1, [(self.color, "Blue"), (self.size, "L")])
        self.assertIn("sales price of these variants changes", wizard_form.preview)
        self.assertFalse(wizard_form.has_errors)

    def test_sale_price_not_kept(self):
        self._skip_if_variant_prices_are_independent()
        self._value(self.size, "L").default_extra_price = 1
        target = self._create_template("Shirt", {self.size: ["M"]}, list_price=10)
        source = self._create_template("Shirt L", list_price=12)
        variant = source.product_variant_ids
        wizard_form = self._open_wizard(source)
        wizard_form.target_tmpl_id = target
        wizard_form.keep_sale_price = False
        self._set_line_values(wizard_form, 0, [(self.size, "L")])
        self.assertIn("sales price of these variants changes", wizard_form.preview)
        wizard_form.save().action_move()
        self.assertEqual(variant.lst_price, 11)
