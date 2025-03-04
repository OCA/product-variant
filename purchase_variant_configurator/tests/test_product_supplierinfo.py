from odoo.tests.common import TransactionCase


class TestProductSupplierinfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SupplierInfo = cls.env["product.supplierinfo"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.Partner = cls.env["res.partner"]

        # Create dummy partners
        cls.partner_1 = cls.Partner.create({"name": "Test Partner 1"})
        cls.partner_2 = cls.Partner.create({"name": "Test Partner 2"})

        # Create product templates
        cls.product_template = cls.ProductTemplate.create(
            {
                "name": "Test Template",
            }
        )
        cls.product_template_2 = cls.ProductTemplate.create(
            {
                "name": "Test Template 2",
            }
        )

        # Create supplier info records
        cls.supplierinfo_1 = cls.SupplierInfo.create(
            {
                "partner_id": cls.partner_1.id,  # Use partner_id instead of name
                "product_tmpl_id": cls.product_template.id,
            }
        )
        cls.supplierinfo_2 = cls.SupplierInfo.create(
            {
                "partner_id": cls.partner_2.id,  # Use partner_id instead of name
                "product_tmpl_id": cls.product_template_2.id,
            }
        )

    def test_search_with_context_pvc_product_tmpl(self):
        """Test search with pvc_product_tmpl context."""
        args = [("product_tmpl_id", "=", "new_id_placeholder")]

        # Search with context that includes 'pvc_product_tmpl'
        supplierinfos = self.SupplierInfo.with_context(
            pvc_product_tmpl=self.product_template.id
        ).search(args)

        # Test that only supplierinfo_1 is returned because it uses product_template
        self.assertIn(
            self.supplierinfo_1,
            supplierinfos,
            "Supplier info for the specified product template should be found.",
        )
        self.assertNotIn(
            self.supplierinfo_2,
            supplierinfos,
            "Supplier info for other product templates should not be found.",
        )

    def test_search_without_context_pvc_product_tmpl(self):
        """Test search without pvc_product_tmpl context."""
        # Search without 'pvc_product_tmpl' context
        args = [("product_tmpl_id", "=", self.product_template.id)]
        supplierinfos = self.SupplierInfo.search(args)

        # Test that supplierinfo_1 is found and supplierinfo_2 is not
        self.assertIn(
            self.supplierinfo_1,
            supplierinfos,
            "Supplier info for the specified product template should be found.",
        )
        self.assertNotIn(
            self.supplierinfo_2,
            supplierinfos,
            "Supplier info for other product templates should not be found.",
        )

    def test_search_with_mixed_args(self):
        """Test search with mixed args."""
        args = [
            ("product_tmpl_id", "=", "new_id_placeholder"),
            ("partner_id", "=", self.partner_1.id),
        ]

        # Use keyword arguments for context
        supplierinfos = self.SupplierInfo.with_context(
            pvc_product_tmpl=self.product_template.id
        ).search(args)

        # The supplierinfo_1 should be returned, but supplierinfo_2 should not
        self.assertIn(
            self.supplierinfo_1,
            supplierinfos,
            "Supplier info should be found when matching multiple criteria.",
        )
        self.assertNotIn(
            self.supplierinfo_2,
            supplierinfos,
            "Supplier info for other templates should not be found.",
        )

    def test_search_with_no_context_and_mixed_args(self):
        """Test search with no context and mixed args."""
        args = [
            ("product_tmpl_id", "=", self.product_template.id),
            ("partner_id", "=", self.partner_1.id),
        ]

        # Search without the pvc_product_tmpl context
        supplierinfos = self.SupplierInfo.search(args)

        # Test that supplierinfo_1 is found and supplierinfo_2 is not
        self.assertIn(
            self.supplierinfo_1,
            supplierinfos,
            "Supplier info for the specified product template should be found.",
        )
        self.assertNotIn(
            self.supplierinfo_2,
            supplierinfos,
            "Supplier info for other product templates should not be found.",
        )
