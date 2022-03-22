# Copyright 2022 ForgeFlow S.L. <https://forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductVariantConfiguratorManualCreation(TransactionCase):
    def setUp(self):
        super().setUp()
