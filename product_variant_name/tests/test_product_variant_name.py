# Copyright 2023 ForgeFlow, S.L.
# Copyright 2026 alb-oca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.fields import Command
from odoo.tests import TransactionCase


class TestProductVariantName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("fr_FR")
        cls.single = cls.env["product.template"].create({"name": "Shackle 1 t"})
        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "Capacity",
                "value_ids": [
                    Command.create({"name": "1 t"}),
                    Command.create({"name": "2 t"}),
                ],
            }
        )
        cls.family = cls.env["product.template"].create(
            {
                "name": "Hoist",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [Command.set(cls.attribute.value_ids.ids)],
                        }
                    )
                ],
            }
        )
        cls.named, cls.unnamed = cls.family.product_variant_ids
        cls.named.name = "Hoist 1 t, lifting height 3 m"

    def setUp(self):
        super().setUp()
        self.product_tmpl_model = self.env["product.template"]
        self.product_model = self.env["product.product"]

    def test_product_variant_name(self):
        # Create a product template and check that variant is created with the
        # same name
        product_tmpl = self.product_tmpl_model.create({"name": "Test Template"})
        self.assertEqual(product_tmpl.product_variant_id.name, product_tmpl.name)
        # Modify variant name and check the difference
        product_tmpl.product_variant_id.write({"name": "Test Variant"})
        self.assertNotEqual(product_tmpl.product_variant_id.name, product_tmpl.name)

    def test_rename_template_in_one_language(self):
        self.single.with_context(lang="fr_FR").name = "Manille droite 1 t"
        variant = self.single.product_variant_ids
        self.assertEqual(
            variant.with_context(lang="fr_FR").name,
            "Manille droite 1 t",
            "The variant should take the new French name",
        )
        self.assertEqual(
            variant.with_context(lang="en_US").name,
            "Shackle 1 t",
            "The variant should keep its English name",
        )

    def test_translate_template_name(self):
        self.single.update_field_translations("name", {"fr_FR": "Manille 1 t"})
        variant = self.single.product_variant_ids
        self.assertEqual(
            variant.with_context(lang="fr_FR").name,
            "Manille 1 t",
            "The variant should take the name given in the translation dialog",
        )

    def test_variant_with_own_name_keeps_it(self):
        self.family.name = "Hoist renamed"
        self.assertEqual(
            self.named.name,
            "Hoist 1 t, lifting height 3 m",
            "A variant with a name of its own should keep it",
        )
        self.assertEqual(
            self.unnamed.name,
            "Hoist renamed",
            "A variant named like its template should follow it",
        )

    def test_archived_variant_follows(self):
        self.unnamed.active = False
        self.family.name = "Hoist renamed"
        self.assertEqual(
            self.unnamed.name,
            "Hoist renamed",
            "An archived variant should follow too",
        )

    def test_rename_while_adding_variants(self):
        self.single.write(
            {
                "name": "Shackle",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [Command.set(self.attribute.value_ids.ids)],
                        }
                    )
                ],
            }
        )
        self.assertEqual(
            set(self.single.product_variant_ids.mapped("name")),
            {"Shackle"},
            "All the variants should take the new name",
        )
