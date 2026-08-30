# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProductVariantChangeAttributeValue(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.legs = cls.env.ref("product.pa_legs", raise_if_not_found=False)
        if not cls.legs:
            cls.legs = cls.env["product.attribute"].create({"name": "Legs"})

        cls.steel = cls.env.ref("product.pav_legs_steel", raise_if_not_found=False)
        if not cls.steel:
            cls.steel = cls.env["product.attribute.value"].create(
                {"name": "Steel", "attribute_id": cls.legs.id}
            )

        cls.aluminium = cls.env.ref(
            "product.pav_legs_aluminium", raise_if_not_found=False
        )
        if not cls.aluminium:
            cls.aluminium = cls.env["product.attribute.value"].create(
                {"name": "Aluminium", "attribute_id": cls.legs.id}
            )

        cls.color = cls.env.ref("product.pa_color", raise_if_not_found=False)
        if not cls.color:
            cls.color = cls.env["product.attribute"].create({"name": "Color"})

        cls.white = cls.env.ref("product.pav_color_white", raise_if_not_found=False)
        if not cls.white:
            cls.white = cls.env["product.attribute.value"].create(
                {"name": "White", "attribute_id": cls.color.id}
            )

        cls.black = cls.env.ref("product.pav_color_black", raise_if_not_found=False)
        if not cls.black:
            cls.black = cls.env["product.attribute.value"].create(
                {"name": "Black", "attribute_id": cls.color.id}
            )

        cls.color.sequence = 1
        cls.legs.sequence = 2

        cls.pink = cls.env["product.attribute.value"].create(
            {"name": "Pink", "attribute_id": cls.color.id}
        )
        cls.blue = cls.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": cls.color.id}
        )
        cls.template = cls.env.ref(
            "product_variant_change_attribute_value.product_product_1_product_template",
            raise_if_not_found=False,
        )
        if not cls.template:
            cls.template = cls.env["product.template"].create(
                {
                    "name": "Custom Desk",
                    "attribute_line_ids": [
                        (
                            0,
                            0,
                            {
                                "attribute_id": cls.legs.id,
                                "value_ids": [(6, 0, [cls.steel.id, cls.aluminium.id])],
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "attribute_id": cls.color.id,
                                "value_ids": [(6, 0, [cls.white.id, cls.black.id])],
                            },
                        ),
                    ],
                }
            )
        cls.variants = cls.template.product_variant_ids

        def _get_variant(legs_val, color_val):
            return cls.variants.filtered(
                lambda v: legs_val
                in v.product_template_attribute_value_ids.product_attribute_value_id
                and color_val
                in v.product_template_attribute_value_ids.product_attribute_value_id
            )

        cls.variant_1 = _get_variant(cls.steel, cls.white)
        cls.variant_2 = _get_variant(cls.steel, cls.black)
        cls.variant_3 = _get_variant(cls.aluminium, cls.white)
        cls.variant_4 = _get_variant(cls.aluminium, cls.black)
        cls.used_values = (
            cls.variants.product_template_attribute_value_ids.product_attribute_value_id
        )
        cls.wiz_model = cls.env["variant.attribute.value.wizard"]

    def _get_wiz(self, prod_ids=None):
        prod_ids = prod_ids or self.variants.ids
        context = {"active_model": "product.product", "active_ids": prod_ids}
        return Form(self.wiz_model.with_context(**context)).save()

    def _change_action(self, wiz, value, attribute_action, replaced_by_id=False):
        """Set an action to do by the wizard on an attribute value."""
        actions = wiz.attributes_action_ids
        action = actions.filtered(lambda r: r.product_attribute_value_id == value)
        action.attribute_action = attribute_action
        action.replaced_by_id = replaced_by_id

    def _is_value_on_variant(self, variant, attribute_value):
        values = variant.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        )
        return attribute_value in values

    def _is_attribute_value_on_template(self, product, attribute_value):
        """Check if an attribute value is assigned to a variant template."""
        template = product.product_tmpl_id
        attribute = attribute_value.attribute_id
        attribute_line = template.attribute_line_ids.filtered(
            lambda x: x.attribute_id == attribute
        )
        if not attribute_line:
            return False
        ptav = self.env["product.template.attribute.value"].search(
            [
                ("attribute_line_id", "=", attribute_line.id),
                ("product_attribute_value_id", "=", attribute_value.id),
            ],
            limit=1,
        )
        if not ptav:
            return False
        # Check that it is also active
        return ptav.ptav_active

    def test_fields(self):
        wiz = self._get_wiz()
        self.assertEqual(wiz.product_ids, self.variants)
        self.assertEqual(wiz.product_variant_count, len(self.variants))
        self.assertEqual(wiz.product_template_count, len(self.variants.product_tmpl_id))
        values = self.steel | self.aluminium | self.white | self.black
        self.assertEqual(wiz.attribute_value_ids, values)
        self.assertEqual(wiz.available_attribute_ids, self.legs | self.color)
        self.assertEqual(len(wiz.attributes_action_ids), len(values))

    def test_actions_field_filter(self):
        wiz = self._get_wiz()
        self.assertEqual(len(wiz.attributes_action_ids), len(wiz.attribute_value_ids))
        with Form(wiz) as res:
            res.filter_attribute_id = self.legs
        self.assertEqual(
            len(res.attributes_action_ids),
            len([x for x in self.legs.value_ids if x in self.used_values]),
        )

    @mute_logger("odoo.models.unlink")
    def test_remove_attribute_value(self):
        """Check removing an attribute value on ALL variants of a template."""
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.steel))

        wiz = self._get_wiz()
        self._change_action(wiz, self.steel, "delete")
        wiz.action_apply()

        self.assertFalse(self._is_value_on_variant(self.variant_1, self.steel))
        self.assertFalse(
            self._is_attribute_value_on_template(self.variant_1, self.steel)
        )

    @mute_logger("odoo.models.unlink")
    def test_remove_all_attribute_values(self):
        """Check removing an attribute value on ALL variants of a template.

        Normally this can cause an error because you cannot delete all values
        if the variants left do not have a unique combination of attributes.
        """
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.steel))

        wiz = self._get_wiz()
        self._change_action(wiz, self.steel, "delete")
        self._change_action(wiz, self.aluminium, "delete")
        wiz.action_apply()
        self.assertFalse(self._is_value_on_variant(self.variant_1, self.steel))
        self.assertFalse(
            self._is_attribute_value_on_template(self.variant_1, self.steel)
        )

    def test_remove_attribute_values_when_both_products_are_associated(self):
        if "sale.order" not in self.env:
            return

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.sale_order_1 = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        self.sale_order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "name": self.variant_1.name,
                "product_id": self.variant_1.id,
                "product_uom_qty": 2,
                "price_unit": 10,
                "customer_lead": 1.0,
            }
        )
        self.sale_order_line_2 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "name": self.variant_3.name,
                "product_id": self.variant_3.id,
                "product_uom_qty": 2,
                "price_unit": 10,
                "customer_lead": 1.0,
            }
        )
        wiz = self._get_wiz()
        self._change_action(wiz, self.steel, "delete")
        self._change_action(wiz, self.aluminium, "delete")
        with self.assertRaises(UserError) as err:
            wiz.action_apply()
        self.assertTrue(
            err.exception.args[0].endswith(
                "with Sale Orders/Invoices/etc., impossible to remove"
            )
        )

    def test_remove_all_attribute_values_when_one_product_is_associated(self):
        if "sale.order" not in self.env:
            return

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        self.sale_order_1 = self.env["sale.order"].create(
            {"partner_id": self.partner.id}
        )
        self.sale_order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_1.id,
                "name": self.variant_1.name,
                "product_id": self.variant_1.id,
                "product_uom_qty": 2,
                "price_unit": 10,
                "customer_lead": 1.0,
            }
        )

        wiz = self._get_wiz()
        self._change_action(wiz, self.steel, "delete")
        self._change_action(wiz, self.aluminium, "delete")
        wiz.action_apply()
        self.assertFalse(self._is_value_on_variant(self.variant_1, self.steel))

    @mute_logger("odoo.models.unlink")
    def test_change_attribute_value(self):
        """Check changing an attribute value on ALL variant of a template."""
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.white))

        wiz = self._get_wiz()
        self._change_action(wiz, self.white, "replace", self.pink)
        wiz.action_apply()

        self.assertFalse(self._is_value_on_variant(self.variant_1, self.white))
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.pink))
        # White has been removed from the template
        self.assertFalse(
            self._is_attribute_value_on_template(self.variant_1, self.white)
        )

    def test_change_attribute_value_2(self):
        """Check changing an attribute value on some variant of a template.

        Changing the value white to pink on variant 3 and 4.
        """
        self.assertTrue(self._is_value_on_variant(self.variant_3, self.white))
        self.assertFalse(self._is_value_on_variant(self.variant_4, self.white))
        # Variant 1 has the white attribute but is is not picked by the wizard
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.white))

        wiz = self._get_wiz([self.variant_3.id, self.variant_4.id])
        self._change_action(wiz, self.white, "replace", self.pink)
        wiz.action_apply()

        self.assertFalse(self._is_value_on_variant(self.variant_3, self.white))
        self.assertFalse(self._is_value_on_variant(self.variant_4, self.white))
        self.assertTrue(self._is_value_on_variant(self.variant_3, self.pink))
        self.assertFalse(self._is_value_on_variant(self.variant_4, self.pink))
        # The value should not be remove from the template because of variant 1
        self.assertTrue(
            self._is_attribute_value_on_template(self.variant_1, self.white)
        )
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.white))

    @mute_logger("odoo.models.unlink")
    def test_active_deactivate_attribute_value_2_step(self):
        """Deactivate a pav and reactivate it in 2 steps.

        Use the wizard to deactivate (not used anymore) the white attribute
        And reactivate it by using it on another variant.

        """
        self.assertTrue(
            self._is_attribute_value_on_template(self.variant_1, self.white)
        )
        self.assertTrue(
            self._is_attribute_value_on_template(self.variant_1, self.black)
        )
        wiz = self._get_wiz()
        self._change_action(wiz, self.white, "replace", self.pink)
        wiz.action_apply()
        self.assertFalse(
            self._is_attribute_value_on_template(self.variant_1, self.white)
        )
        self._change_action(wiz, self.black, "replace", self.white)
        wiz.action_apply()
        self.assertTrue(
            self._is_attribute_value_on_template(self.variant_1, self.white)
        )
        self.assertFalse(
            self._is_attribute_value_on_template(self.variant_1, self.black)
        )

    @mute_logger("odoo.models.unlink")
    def test_active_deactivate_attribute_value_1_step(self):
        """Deactivate a pav and reactivate it in 1 steps.

        Same than previous tests but both replacement are done in one
        execution of the wizard.
        """
        self.assertEqual(
            sorted(self.variants.mapped("display_name")),
            sorted(
                [
                    "Custom Desk (Black, Aluminium)",
                    "Custom Desk (Black, Steel)",
                    "Custom Desk (White, Aluminium)",
                    "Custom Desk (White, Steel)",
                ]
            ),
        )
        wiz = self._get_wiz()
        self._change_action(wiz, self.white, "replace", self.pink)
        self._change_action(wiz, self.black, "replace", self.white)
        wiz.action_apply()
        self.assertTrue(
            self._is_attribute_value_on_template(self.variant_1, self.white)
        )
        self.assertFalse(
            self._is_attribute_value_on_template(self.variant_1, self.black)
        )
        self.assertEqual(
            sorted(self.variants.mapped("display_name")),
            sorted(
                [
                    "Custom Desk (Pink, Aluminium)",
                    "Custom Desk (Pink, Steel)",
                    "Custom Desk (White, Aluminium)",
                    "Custom Desk (White, Steel)",
                ]
            ),
        )

    def test_default_get_non_product_model(self):
        """Test default_get when active_model is not product.product."""
        res = self.wiz_model.with_context(active_model="res.partner").default_get(
            ["product_variant_count"]
        )
        self.assertNotIn("product_ids", res)

    def test_selectable_attribute_value_ids(self):
        """Test compute of selectable_attribute_value_ids on action model."""
        wiz = self._get_wiz()
        action = wiz.attributes_action_ids[0]
        self.assertTrue(action.selectable_attribute_value_ids)

        empty_action = self.env["variant.attribute.value.action"].create(
            {"attribute_action": "do_nothing"}
        )
        self.assertFalse(empty_action.selectable_attribute_value_ids)

    def test_replace_without_replacement_value(self):
        """Test setting replace action without specifying replaced_by_id."""
        wiz = self._get_wiz()
        self._change_action(wiz, self.white, "replace", replaced_by_id=False)
        wiz.action_apply()
        self.assertTrue(self._is_value_on_variant(self.variant_1, self.white))

    def test_replace_with_new_attribute(self):
        """Test replacing an attribute value with a value from an
        attribute not on the template."""
        material_attr = self.env["product.attribute"].create({"name": "Material"})
        wood_val = self.env["product.attribute.value"].create(
            {"name": "Wood", "attribute_id": material_attr.id}
        )
        wiz = self._get_wiz()
        self._change_action(wiz, self.white, "replace", replaced_by_id=wood_val)
        wiz.action_apply()
        self.assertTrue(self._is_value_on_variant(self.variant_1, wood_val))

    def test_remove_duplicate_product_both_associated(self):
        """Test error raised when trying to remove duplicate variants
        and both are associated."""
        if "sale.order" not in self.env:
            return
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        so1 = self.env["sale.order"].create({"partner_id": partner.id})
        self.env["sale.order.line"].create(
            {"order_id": so1.id, "product_id": self.variant_1.id}
        )
        so2 = self.env["sale.order"].create({"partner_id": partner.id})
        self.env["sale.order.line"].create(
            {"order_id": so2.id, "product_id": self.variant_3.id}
        )
        wiz = self._get_wiz()
        self._change_action(wiz, self.steel, "delete")
        self._change_action(wiz, self.aluminium, "delete")
        with self.assertRaises(UserError):
            wiz.action_apply()

    def test_remove_duplicate_product_product_associated_check_product_not(self):
        """Test duplicate product removal when target product is
        associated but check product is not."""
        if "sale.order" not in self.env:
            return
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        so = self.env["sale.order"].create({"partner_id": partner.id})
        self.env["sale.order.line"].create(
            {"order_id": so.id, "product_id": self.variant_3.id}
        )
        wiz = self._get_wiz()
        self._change_action(wiz, self.steel, "delete")
        self._change_action(wiz, self.aluminium, "delete")
        wiz.action_apply()
        self.assertTrue(self.variant_3.exists())
        self.assertFalse(self.variant_1.exists())

    def test_remove_duplicate_product_default_ptav(self):
        """Test _remove_duplicate_product with default ptav_ids."""
        wiz = self._get_wiz()
        res = wiz._remove_duplicate_product(self.variant_1)
        self.assertFalse(res)

    def test_handle_unique_violation(self):
        """Test _handle_unique_violation error handling."""
        import psycopg2

        wiz = self._get_wiz()

        class MockUniqueViolation(psycopg2.IntegrityError):
            pgcode = psycopg2.errorcodes.UNIQUE_VIOLATION

        class MockOtherIntegrityError(psycopg2.IntegrityError):
            pgcode = "12345"

        def raise_unique():
            raise MockUniqueViolation()

        with self.assertRaises(UserError):
            wiz._handle_unique_violation(raise_unique, "Custom Error")

        def raise_other():
            raise MockOtherIntegrityError()

        with self.assertRaises(psycopg2.IntegrityError):
            wiz._handle_unique_violation(raise_other, "Custom Error")

    def test_cleanup_attribute_values_deactivate_line(self):
        """Test _cleanup_attribute_values deactivates line when no values left."""
        wiz = self._get_wiz()
        legs_line = self.template.attribute_line_ids.filtered(
            lambda x: x.attribute_id == self.legs
        )
        self.assertTrue(legs_line.active)
        wiz._cleanup_attribute_values(
            self.variant_1, {self.legs: self.steel | self.aluminium}
        )
        self.assertFalse(legs_line.active)

    def test_remove_duplicate_product_unlinked_check_product(self):
        """Test _remove_duplicate_product skips unlinked check_product (line 217)."""
        wiz = self._get_wiz()
        self.variant_2.unlink()
        res = wiz._remove_duplicate_product(self.variant_1)
        self.assertFalse(res)

    def test_remove_duplicate_both_associated_mock(self):
        """Test UserError raised when both products are associated (lines 224-232)."""
        from unittest.mock import patch

        wiz = self._get_wiz()
        with patch.object(wiz.__class__, "_is_product_associated", return_value=True):
            target_ptavs = self.variant_2.product_template_attribute_value_ids
            with self.assertRaises(UserError):
                wiz._remove_duplicate_product(self.variant_1, target_ptavs)

    def test_is_product_associated_true(self):
        """Test _is_product_associated returns True when model search
        finds line (lines 247-248)."""
        from unittest.mock import patch

        wiz = self._get_wiz()
        mock_model = self.env["ir.model"].search(
            [("model", "=", "res.partner")], limit=1
        )
        with patch.object(
            self.env["ir.model"].__class__, "search", return_value=mock_model
        ):
            with patch.object(
                self.env["res.partner"].__class__,
                "search",
                return_value=self.env["res.partner"].browse(1),
            ):
                self.assertTrue(wiz._is_product_associated(self.variant_1))
