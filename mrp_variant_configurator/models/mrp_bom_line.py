# Copyright 2017 Jose Luis Sandoval Alaguna <jose.alaguna@rotafilo.com.tr>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class MrpBomLine(models.Model):
    _inherit = ['mrp.bom.line', 'product.configurator']
    _name = 'mrp.bom.line'
