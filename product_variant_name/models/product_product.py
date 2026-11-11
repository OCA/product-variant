# Copyright 2023 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    name = fields.Char(index="trigram", required=True, translate=True)

    @api.model_create_multi
    def create(self, vals_list):
        """Name the template of a variant created without template.

        ``name`` being a field of the variant, the template created by
        ``_inherits`` (e.g. from a ``product.product`` XML record) would
        otherwise have no name.
        """
        to_create = [
            vals
            for vals in vals_list
            if vals.get("name") and not vals.get("product_tmpl_id")
        ]
        if to_create:
            template_vals_list = []
            for vals in to_create:
                template_vals = {"name": vals["name"]}
                for key in list(vals):
                    field = self._fields.get(key)
                    if field and field.inherited:
                        template_vals[key] = vals.pop(key)
                template_vals_list.append(template_vals)
            templates = (
                self.env["product.template"]
                .with_context(create_product_product=False)
                .create(template_vals_list)
            )
            for vals, template in zip(to_create, templates, strict=True):
                vals["product_tmpl_id"] = template.id
        return super().create(vals_list)
