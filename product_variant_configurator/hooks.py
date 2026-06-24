# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.models import NewId


def _patch_many2one_no_wrap_existing_parent():
    """Patch ``Many2one.convert_to_cache`` so that linking a new child
    record to an existing parent through a delegate (``_inherits``) field
    keeps the parent's real id instead of wrapping it in :class:`NewId`.

    The standard Odoo behaviour wraps the parent id whenever the child
    record is new, on the assumption that the parent is being created
    together with the child.  That fits Odoo's native flow (a new
    variant auto-created alongside a new template) but breaks the
    variant configurator's flow where a new variant is attached to an
    *existing* template: the wrap then makes
    ``Field._compute_company_dependent`` reads on the parent return
    empty, because its result dict is keyed by real ids while the loop
    uses the record's ``NewId`` as the lookup key.
    """
    if getattr(fields.Many2one, "_no_wrap_existing_parent_patched", False):
        return
    _original_convert_to_cache = fields.Many2one.convert_to_cache

    def convert_to_cache(self, value, record, validate=True):
        if (
            self.delegate
            and record
            and not any(record._ids)
            and isinstance(value, int)
            and not isinstance(value, NewId)
            and value > 0
        ):
            return value
        return _original_convert_to_cache(self, value, record, validate)

    fields.Many2one.convert_to_cache = convert_to_cache
    fields.Many2one._no_wrap_existing_parent_patched = True


_patch_many2one_no_wrap_existing_parent()
