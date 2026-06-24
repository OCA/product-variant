from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from .fake_models import ProductTemplate as _TestProductTemplate


@tagged("post_install", "-at_install")
class TestCompanyDependentInherited(TransactionCase):
    _test_field_name = "x_test_cd_partner"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _TestProductTemplate._build_model(cls.env.registry, cls.env.cr)
        cls.env.registry.setup_models(cls.env.cr)
        ctx = dict(cls.env.context, update_custom_fields=True)
        cls.env.registry.init_models(cls.env.cr, ["product.template"], ctx)

        cls.partner_a = cls.env["res.partner"].create({"name": "Partner A"})
        cls.partner_default = cls.env["res.partner"].create({"name": "Partner Default"})
        cls.tmpl = cls.env["product.template"].create(
            {"name": "Tpl A", "no_create_variants": "yes"}
        )
        cls.tmpl.x_test_cd_partner = cls.partner_a

    @classmethod
    def tearDownClass(cls):
        Template = cls.env["product.template"]
        if cls._test_field_name in Template._fields:
            Template._pop_field(cls._test_field_name)
        cls.env.registry.setup_models(cls.env.cr)
        super().tearDownClass()

    def test_new_variant_keeps_existing_template_id_unwrapped(self):
        new_variant = self.env["product.product"].new({"product_tmpl_id": self.tmpl.id})
        self.assertEqual(new_variant.product_tmpl_id, self.tmpl)
        self.assertEqual(new_variant.product_tmpl_id._ids, (self.tmpl.id,))

    def test_new_variant_reads_template_company_dependent_value(self):
        new_variant = self.env["product.product"].new({"product_tmpl_id": self.tmpl.id})
        self.assertEqual(new_variant.x_test_cd_partner, self.partner_a)

    def test_new_variant_reads_template_value_over_company_default(self):
        self.env["ir.property"]._set_default(
            self._test_field_name,
            "product.template",
            self.partner_default,
        )
        new_variant = self.env["product.product"].new({"product_tmpl_id": self.tmpl.id})
        self.assertEqual(new_variant.x_test_cd_partner, self.partner_a)
