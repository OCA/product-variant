# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import common


class TestProductVariantChangeAttributeValue(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.legs = cls.env.ref("product.product_attribute_1")
        cls.steel = cls.env.ref("product.product_attribute_value_1")
        cls.aluminium = cls.env.ref("product.product_attribute_value_2")

        cls.color = cls.env.ref("product.product_attribute_2")
        cls.white = cls.env.ref("product.product_attribute_value_3")
        cls.black = cls.env.ref("product.product_attribute_value_4")
        cls.pink = cls.env["product.attribute.value"].create(
            {"name": "Pink", "attribute_id": cls.color.id}
        )
        cls.blue = cls.env["product.attribute.value"].create(
            {"name": "Blue", "attribute_id": cls.color.id}
        )

        cls.variant_1 = cls.env.ref("product.product_product_4")
        cls.variant_2 = cls.env.ref("product.product_product_4b")
        cls.variant_3 = cls.env.ref("product.product_product_4c")
        cls.variant_4 = cls.env.ref("product.product_product_4d")
        cls.variant_ids = [
            cls.variant_1.id,
            cls.variant_2.id,
            cls.variant_3.id,
            cls.variant_4.id,
        ]
        cls.template = cls.variant_1.product_tmpl_id
        assert len(cls.template.product_variant_ids) == 4

        cls.wiz_model = cls.env["variant.attribute.value.wizard"]

    def _get_wiz(self, prod_ids=None):
        prod_ids = prod_ids or self.variant_ids
        return self.wiz_model.with_context(default_product_ids=prod_ids).create({})

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
            lambda l: l.attribute_id == attribute
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

    def test_change_attribure_value(self):
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

    def test_active_deactivate_attribute_value_2_step(self):
        """ Deactivate a pav and reactivate it in 2 steps.

        Use the wizard to desactivate (not used anymore) the white attribute
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

    def test_active_deactivate_attribute_value_1_step(self):
        """ Deactivate a pav and reactivate it in 1 steps.

        Same than previous tests but both replacement are done in one
        execution of the wizard.

        """
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
