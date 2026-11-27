# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models

SKIP_VARIANT_SYNC = "product_variant_change_template_skip_variant_sync"


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _create_variant_ids(self):
        # While variants are being moved the attribute configuration is
        # temporarily inconsistent: the core synchronization would create,
        # archive or delete variants based on that intermediate state.
        if self.env.context.get(SKIP_VARIANT_SYNC):
            return True
        return super()._create_variant_ids()
