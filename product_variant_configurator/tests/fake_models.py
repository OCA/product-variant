from odoo import fields, models


class ProductTemplate(models.Model):
    # Test-only company_dependent field
    _inherit = "product.template"  # pylint: disable=consider-merging-classes-inherited

    x_test_cd_partner = fields.Many2one(
        comodel_name="res.partner",
        string="Test CD Partner",
        company_dependent=True,
    )
