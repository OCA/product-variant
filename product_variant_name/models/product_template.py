# Copyright 2023 ForgeFlow, S.L.
# Copyright 2026 alb-oca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from collections import defaultdict

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        if "name" not in vals:
            return super().write(vals)
        mirrors = self._get_variant_name_mirrors()
        res = super().write(vals)
        self._sync_variant_names(mirrors)
        return res

    def update_field_translations(self, field_name, translations, source_lang=""):
        """Same as write(), for the translation dialog, which does not call it."""
        if field_name != "name":
            return super().update_field_translations(
                field_name, translations, source_lang=source_lang
            )
        mirrors = self._get_variant_name_mirrors()
        res = super().update_field_translations(
            field_name, translations, source_lang=source_lang
        )
        self._sync_variant_names(mirrors)
        return res

    def _prepare_variant_values(self, combination):
        variant_dict = super()._prepare_variant_values(combination)
        variant_dict["name"] = self.name
        return variant_dict

    def _get_variant_name_mirrors(self):
        """Variants still named like their template, per language. Call it before
        writing the new name: afterwards, they look like variants named on purpose."""
        mirrors = defaultdict(dict)
        for lang, _lang_name in self.env["res.lang"].get_installed():
            # archived variants too: once restored, they still follow
            for template in self.with_context(lang=lang, active_test=False):
                variants = template.product_variant_ids.filtered(
                    lambda variant, name=template.name: variant.name == name
                )
                if variants:
                    mirrors[lang][template.id] = variants.ids
        return mirrors

    def _sync_variant_names(self, mirrors):
        # the same write can unlink variants
        alive_ids = set(self.with_context(active_test=False).product_variant_ids.ids)
        for lang, variant_ids_by_template in mirrors.items():
            products = self.env["product.product"].with_context(lang=lang)
            for template in self.with_context(lang=lang):
                variant_ids = variant_ids_by_template.get(template.id, [])
                products.browse(alive_ids.intersection(variant_ids)).filtered(
                    lambda variant, name=template.name: variant.name != name
                ).write({"name": template.name})
