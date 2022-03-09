# Copyright 2020 Studio73 - Miguel Gandia

from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _grid_header_cell(self, fro_currency, to_currency, company, display_extra=True):
        header_cell = super()._grid_header_cell(
            fro_currency, to_currency, company, display_extra
        )
        header_cell.update(
            {"html_color": self[0].html_color if self and self[0].html_color else False}
        )
        return header_cell
