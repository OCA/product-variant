# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.model_create_multi
    def create(self, vals_list):
        """Link created attribute value to the associated template if proceed.

        This happens when quick-creating values from the product configurator.
        """
        attr_values = super(ProductAttributeValue, self).create(vals_list)
        if "template_for_attribute_value" in self.env.context:
            template = self.env["product.template"].browse(
                self.env.context["template_for_attribute_value"]
            )
            for attr in attr_values:
                line = template.attribute_line_ids.filtered(
                    lambda x: x.attribute_id == attr.attribute_id
                )
                line.value_ids = [(4, attr.id)]
        return attr_values
