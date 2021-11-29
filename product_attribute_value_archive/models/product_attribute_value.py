# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    active = fields.Boolean(default=True)

    def _get_related_variants(self):
        """Returns all related archived products.

        When product is referenced from a SO, the variant is archived instead
        of unlinked when it becomes not necessary. Thus, it can happen
        that a product.attribute.value is still referenced by an archived
        product.
        """
        self.ensure_one()
        self.flush()
        query = """
            SELECT array_agg(pp.id)
            FROM product_product pp
            JOIN product_variant_combination pvc
              ON pp.id = pvc.product_product_id
            JOIN product_template_attribute_value ptav
              ON pvc.product_template_attribute_value_id = ptav.id
            JOIN product_attribute_value pav
              ON pav.id = ptav.product_attribute_value_id
            WHERE pav.id = %(value_id)s;
        """
        self.env.cr.execute(query, {"value_id": self.id})
        # result is `[(None,)]` if nothing matched, `[([ids],)]` otherwise
        product_ids = self.env.cr.fetchall()[0][0]
        return self.env["product.product"].browse(product_ids)

    def _archive(self):
        return self.write({"active": False})

    def _unarchive(self):
        return self.write({"active": True})

    def _get_pav_to_archive(self):
        pav_to_archive_ids = set()
        for pav in self:
            related_variants = pav._get_related_variants()
            # Archive only if all related variants are archived
            # (none is active)
            all_variants_are_archived = related_variants and not any(
                related_variants.mapped("active")
            )
            if all_variants_are_archived:
                pav_to_archive_ids.add(pav.id)
        return self.browse(pav_to_archive_ids)

    def unlink(self):
        pav_to_archive = self._get_pav_to_archive()
        pav_to_unlink = self - pav_to_archive
        if pav_to_archive:
            pav_to_archive._archive()
        return super(ProductAttributeValue, pav_to_unlink).unlink()

    @api.model_create_multi
    def create(self, values):
        values_to_create = []
        unarchived_record_ids = set()
        for value in values:
            existing_archived_value = self.search(
                [
                    ("active", "=", False),
                    ("name", "=", value["name"]),
                    ("attribute_id", "=", value["attribute_id"]),
                ]
            )
            if existing_archived_value:
                existing_archived_value.active = True
                unarchived_record_ids.add(existing_archived_value.id)
                continue
            values_to_create.append(value)
        created_records = super().create(values_to_create)
        return created_records | self.browse(unarchived_record_ids)
