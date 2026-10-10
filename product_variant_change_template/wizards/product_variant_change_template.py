# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import itertools
import math
from collections import defaultdict

from markupsafe import Markup, escape
from psycopg2.errors import LockNotAvailable

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import SQL, float_compare, float_round, mute_logger

from ..models.product_template import SKIP_VARIANT_SYNC

MAX_ENUMERATED_COMBINATIONS = 100000


class _SimulationRollback(Exception):
    """Raised to roll back the savepoint of a variant sync simulation."""


class _MergeAbort(Exception):
    """Raised when a source template cannot be merged into the target."""


class ProductVariantChangeTemplate(models.TransientModel):
    _name = "product.variant.change.template"
    _description = "Move product variants to another template"

    source_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        relation="product_variant_change_template_source_rel",
        string="Source Templates",
    )
    include_archived = fields.Boolean(
        string="Include Archived Variants",
        help="Also move the archived variants of the source templates.",
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="product_variant_change_template_product_rel",
        string="Variants to Move",
        compute="_compute_product_ids",
        store=True,
        readonly=False,
        context={"active_test": False},
    )
    target_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Target Template",
    )
    line_ids = fields.One2many(
        comodel_name="product.variant.change.template.line",
        inverse_name="wizard_id",
        string="Variants",
        compute="_compute_line_ids",
        store=True,
        readonly=False,
    )
    attribute_default_ids = fields.One2many(
        comodel_name="product.variant.change.template.attribute",
        inverse_name="wizard_id",
        string="Values for Existing Variants",
        compute="_compute_attribute_default_ids",
        store=True,
        readonly=False,
    )
    missing_combination_policy = fields.Selection(
        selection=[("exclude", "Exclude them"), ("create", "Create them")],
        string="Missing Combinations",
        default="exclude",
        required=True,
        help="Adding values to the target template makes combinations possible "
        "that no variant uses. 'Exclude them' adds attribute exclusions so Odoo "
        "never generates them; combinations that cannot be excluded without "
        "excluding an existing variant are created anyway. 'Create them' "
        "generates every missing combination, as Odoo does by default.",
    )
    source_template_policy = fields.Selection(
        selection=[("archive", "Archive"), ("merge", "Merge into the target")],
        string="Emptied Source Templates",
        default="archive",
        required=True,
        help="What to do with a source template left without variants. "
        "'Merge' repoints its remaining references (chatter, attachments, "
        "external identifiers, links from other products) to the target and "
        "deletes it; when that is not possible it is archived instead.",
    )
    keep_sale_price = fields.Boolean(
        string="Keep Sales Prices",
        default=True,
        help="Set the extra price of the attribute values added to the target "
        "so the moved variants keep their sales price when possible, and keep "
        "the price of the existing target variants when they get a new "
        "attribute.",
    )
    copy_no_variant_attributes = fields.Boolean(
        string="Copy Non-Variant Attributes",
        default=True,
        help="Add the attributes that do not create variants of the source "
        "templates to the target template.",
    )
    preview = fields.Html(compute="_compute_preview", sanitize=False)
    has_errors = fields.Boolean(compute="_compute_preview")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids") or []
        if active_model == "product.template":
            res["source_tmpl_ids"] = [Command.set(active_ids)]
        elif active_model == "product.product":
            res["product_ids"] = [Command.set(active_ids)]
        return res

    @api.depends("source_tmpl_ids", "include_archived")
    def _compute_product_ids(self):
        for wizard in self:
            if not wizard.source_tmpl_ids:
                wizard.product_ids = wizard.product_ids
                continue
            variants = wizard.source_tmpl_ids.with_context(
                active_test=False
            ).product_variant_ids
            wizard.product_ids = variants.filtered(
                lambda p, w=wizard: p.active or w.include_archived
            )

    @api.depends("product_ids", "target_tmpl_id")
    def _compute_line_ids(self):
        for wizard in self:
            commands = [Command.clear()]
            for product in wizard.product_ids._origin:
                values = wizard._get_default_target_values(product)
                commands.append(
                    Command.create(
                        {
                            "product_id": product.id,
                            "value_ids": [Command.set(values.ids)],
                        }
                    )
                )
            wizard.line_ids = commands

    @api.depends("line_ids.value_ids", "target_tmpl_id")
    def _compute_attribute_default_ids(self):
        for wizard in self:
            chosen = {d.attribute_id: d.value_id for d in wizard.attribute_default_ids}
            commands = [Command.clear()]
            if wizard.target_tmpl_id.with_context(
                active_test=False
            ).product_variant_ids:
                for attribute in wizard._get_new_attributes():
                    commands.append(
                        Command.create(
                            {
                                "attribute_id": attribute.id,
                                "value_id": chosen.get(attribute, False)
                                and chosen[attribute].id,
                            }
                        )
                    )
            wizard.attribute_default_ids = commands

    @api.depends(
        "target_tmpl_id",
        "line_ids.value_ids",
        "attribute_default_ids.value_id",
        "missing_combination_policy",
        "source_template_policy",
        "copy_no_variant_attributes",
        "keep_sale_price",
    )
    def _compute_preview(self):
        for wizard in self:
            plan = wizard._prepare_plan()
            wizard.has_errors = bool(plan["errors"])
            wizard.preview = wizard._render_preview(plan)

    def _get_default_target_values(self, product):
        """Keep the values the variant already has and complete the attributes
        the target template only allows with a single value."""
        self.ensure_one()
        values = product.product_template_attribute_value_ids.product_attribute_value_id
        target_lines = self._get_variant_lines(self.target_tmpl_id._origin)
        for line in target_lines:
            if (
                line.attribute_id not in values.attribute_id
                and len(line.value_ids) == 1
            ):
                values |= line.value_ids
        return values

    def _get_new_attributes(self):
        self.ensure_one()
        current = self._get_variant_lines(self.target_tmpl_id._origin).attribute_id
        return self.line_ids.value_ids._origin.attribute_id - current

    @api.model
    def _get_variant_lines(self, template):
        lines = template.valid_product_template_attribute_line_ids
        return lines._without_no_variant_attributes()

    @api.model
    def _get_template_configuration(self, template):
        """Return the variant-creating configuration as ``{attribute id: {value
        ids}}``."""
        return {
            line.attribute_id.id: set(line.value_ids.ids)
            for line in self._get_variant_lines(template)
        }

    @api.model
    def _get_combination(self, product):
        return frozenset(
            product.product_template_attribute_value_ids.product_attribute_value_id.ids
        )

    @api.model
    def _get_excluded_value_pairs(self, template):
        """Return the exclusions of the template as pairs of attribute value ids."""
        pairs = set()
        exclusions = self.env["product.template.attribute.exclusion"].search(
            [
                ("product_tmpl_id", "=", template.id),
                (
                    "product_template_attribute_value_id.product_tmpl_id",
                    "=",
                    template.id,
                ),
            ]
        )
        for exclusion in exclusions:
            value = exclusion.product_template_attribute_value_id
            if not value.ptav_active:
                continue
            for other in exclusion.value_ids.filtered("ptav_active"):
                pairs.add(
                    frozenset(
                        (
                            value.product_attribute_value_id.id,
                            other.product_attribute_value_id.id,
                        )
                    )
                )
        return pairs

    @api.model
    def _get_possible_combinations(self, configuration, excluded_pairs):
        """Return every combination the configuration allows, as frozensets of
        attribute value ids. A configuration without attributes allows the
        empty combination, like the core does."""
        value_lists = [sorted(values) for values in configuration.values()]
        if (
            math.prod(len(values) for values in value_lists)
            > MAX_ENUMERATED_COMBINATIONS
        ):
            raise UserError(
                _(
                    "The resulting attribute configuration allows more than "
                    "%(limit)s combinations.",
                    limit=MAX_ENUMERATED_COMBINATIONS,
                )
            )
        combinations = set()
        for combination in itertools.product(*value_lists):
            if excluded_pairs and any(
                frozenset(pair) in excluded_pairs
                for pair in itertools.combinations(combination, 2)
            ):
                continue
            combinations.add(frozenset(combination))
        return combinations

    @api.model
    def _resolve_missing_combinations(
        self, possible, missing, preferred_values, exclude=True
    ):
        """Split the missing combinations into value pairs to exclude and
        combinations to create.

        Exclusions work on pairs of values, so a pair is only valid when every
        possible combination containing it is missing; otherwise it would hide
        an existing variant.
        """
        ordered = sorted(missing, key=sorted)
        if not exclude:
            return set(), ordered
        pairs = set()
        to_create = []
        for combination in ordered:
            if any(pair <= combination for pair in pairs):
                continue
            candidates = sorted(
                (
                    frozenset(pair)
                    for pair in itertools.combinations(sorted(combination), 2)
                ),
                key=lambda pair: (not pair & preferred_values, sorted(pair)),
            )
            for pair in candidates:
                if all(other in missing for other in possible if pair <= other):
                    pairs.add(pair)
                    break
            else:
                to_create.append(combination)
        return pairs, to_create

    @api.model
    def _get_no_variant_additions(self, target, sources):
        current = {
            line.attribute_id.id: set(line.value_ids.ids)
            for line in target.attribute_line_ids
        }
        additions = defaultdict(set)
        for line in sources.attribute_line_ids:
            if line.attribute_id.create_variant != "no_variant":
                continue
            additions[line.attribute_id.id] |= set(line.value_ids.ids) - current.get(
                line.attribute_id.id, set()
            )
        return {a: v for a, v in additions.items() if v}

    @api.model
    def _get_blocking_fields(self):
        """Template fields whose difference would corrupt the history of the
        moved variants (quantities, valuation, traceability)."""
        fields_list = ["type", "uom_id", "company_id"]
        template_fields = self.env["product.template"]._fields
        return fields_list + [
            f for f in ("is_storable", "tracking") if f in template_fields
        ]

    @api.model
    def _get_warning_fields(self):
        """Template fields the moved variants will take from the target."""
        candidates = (
            "categ_id",
            "uom_po_id",
            "taxes_id",
            "supplier_taxes_id",
            "sale_ok",
            "purchase_ok",
            "route_ids",
            "invoice_policy",
            "purchase_method",
            "property_account_income_id",
            "property_account_expense_id",
        )
        template_fields = self.env["product.template"]._fields
        return [f for f in candidates if f in template_fields]

    @api.model
    def _get_category_blocking_fields(self):
        category_fields = self.env["product.category"]._fields
        return [
            f
            for f in ("property_cost_method", "property_valuation")
            if f in category_fields
        ]

    @api.model
    def _get_field_label(self, model, field_name):
        return model._fields[field_name]._description_string(self.env)

    def _check_template_compatibility(self, source, errors, warnings):
        target = self.target_tmpl_id._origin
        for field_name in self._get_blocking_fields():
            if source[field_name] != target[field_name]:
                errors.append(
                    _(
                        "%(origin)s and %(target)s have a different %(field)s.",
                        origin=source.display_name,
                        target=target.display_name,
                        field=self._get_field_label(target, field_name),
                    )
                )
        for field_name in self._get_category_blocking_fields():
            if source.categ_id[field_name] != target.categ_id[field_name]:
                errors.append(
                    _(
                        "The categories of %(origin)s and %(target)s have a "
                        "different %(field)s.",
                        origin=source.display_name,
                        target=target.display_name,
                        field=self._get_field_label(source.categ_id, field_name),
                    )
                )
        different = [
            self._get_field_label(target, field_name)
            for field_name in self._get_warning_fields()
            if source[field_name] != target[field_name]
        ]
        if different:
            warnings.append(
                _(
                    "The moved variants of %(origin)s will use the %(fields)s "
                    "of %(target)s.",
                    origin=source.display_name,
                    target=target.display_name,
                    fields=", ".join(different),
                )
            )

    def _prepare_plan(self):  # noqa: C901
        """Compute every change the move implies without writing anything."""
        self.ensure_one()
        plan = {
            "errors": [],
            "warnings": [],
            "moves": {},
            "value_additions": {},
            "no_variant_additions": {},
            "price_extras": {},
            "source_combinations": {},
            "configuration": {},
            "defaults": {},
            "target_existing": self.env["product.product"],
            "exclusions": {},
            "creations": {},
            "source_removals": {},
            "emptied_sources": self.env["product.template"],
            "sources": self.env["product.template"],
        }
        errors, warnings = plan["errors"], plan["warnings"]
        target = self.target_tmpl_id._origin
        lines = self.line_ids
        if not target or not lines:
            errors.append(_("Select a target template and at least one variant."))
            return plan
        moved = lines.product_id._origin
        if len(moved) != len(lines):
            errors.append(_("A variant is listed more than once."))
        if moved.filtered(lambda p: p.product_tmpl_id == target):
            errors.append(_("Some variants already belong to the target template."))
            return plan
        sources = moved.product_tmpl_id
        plan["sources"] = sources
        for source in sources:
            self._check_template_compatibility(source, errors, warnings)
        # Target configuration
        configuration = self._get_template_configuration(target)
        plan["configuration"] = configuration
        final_configuration = defaultdict(set)
        for attribute_id, value_ids in configuration.items():
            final_configuration[attribute_id] |= value_ids
        final_attributes = set(configuration) | set(
            lines.value_ids._origin.attribute_id.ids
        )
        for line in lines:
            product = line.product_id._origin
            values = line.value_ids._origin
            if len(values.attribute_id) != len(values):
                errors.append(
                    _(
                        "%(variant)s has several values for the same attribute.",
                        variant=product.display_name,
                    )
                )
                continue
            missing = final_attributes - set(values.attribute_id.ids)
            if missing:
                errors.append(
                    _(
                        "%(variant)s needs a value for %(attributes)s.",
                        variant=product.display_name,
                        attributes=", ".join(
                            self.env["product.attribute"].browse(missing).mapped("name")
                        ),
                    )
                )
                continue
            plan["moves"][product] = frozenset(values.ids)
            plan["source_combinations"][product] = self._get_combination(product)
            for value in values:
                final_configuration[value.attribute_id.id].add(value.id)
        target_existing = target.with_context(active_test=False).product_variant_ids
        plan["target_existing"] = target_existing
        new_attributes = final_attributes - set(configuration)
        defaults = {}
        if new_attributes and target_existing:
            for default in self.attribute_default_ids:
                if default.value_id:
                    defaults[default.attribute_id._origin.id] = (
                        default.value_id._origin.id
                    )
            missing = new_attributes - set(defaults)
            if missing:
                errors.append(
                    _(
                        "Choose the value the existing variants of %(target)s "
                        "take for %(attributes)s.",
                        target=target.display_name,
                        attributes=", ".join(
                            self.env["product.attribute"].browse(missing).mapped("name")
                        ),
                    )
                )
            for attribute_id, value_id in defaults.items():
                if attribute_id in new_attributes:
                    final_configuration[attribute_id].add(value_id)
        plan["defaults"] = {a: v for a, v in defaults.items() if a in new_attributes}
        plan["value_additions"] = {
            attribute_id: values - configuration.get(attribute_id, set())
            for attribute_id, values in final_configuration.items()
            if values - configuration.get(attribute_id, set())
        }
        if self.copy_no_variant_attributes:
            plan["no_variant_additions"] = self._get_no_variant_additions(
                target, sources
            )
        if errors:
            return plan
        # Collisions
        existing_combinations = {}
        for variant in target_existing:
            combination = self._get_combination(variant) | frozenset(
                plan["defaults"].values()
            )
            existing_combinations[combination] = variant
        for variant, combination in plan["moves"].items():
            other = existing_combinations.get(combination)
            if other:
                errors.append(
                    _(
                        "%(variant)s would get the same attributes as %(other)s.",
                        variant=variant.display_name,
                        other=other.display_name,
                    )
                )
            existing_combinations[combination] = variant
        if errors:
            return plan
        policy_exclude = self.missing_combination_policy == "exclude"
        if not target.has_dynamic_attributes():
            excluded = self._get_excluded_value_pairs(target)
            possible_after = self._get_possible_combinations(
                dict(final_configuration), excluded
            )
            for variant, combination in plan["moves"].items():
                if combination not in possible_after:
                    errors.append(
                        _(
                            "An attribute exclusion of %(target)s forbids the "
                            "combination of %(variant)s.",
                            target=target.display_name,
                            variant=variant.display_name,
                        )
                    )
            if errors:
                return plan
            missing_before = self._get_possible_combinations(
                configuration, excluded
            ) - {self._get_combination(v) for v in target_existing}
            missing_after = possible_after - set(existing_combinations)
            added_values = set().union(*plan["value_additions"].values())
            pairs, creations = self._resolve_missing_combinations(
                possible_after,
                missing_after - missing_before,
                added_values,
                exclude=policy_exclude,
            )
            plan["exclusions"][target] = pairs
            plan["creations"][target] = creations
        # Sources
        for source in sources:
            remaining = (
                source.with_context(active_test=False).product_variant_ids - moved
            )
            if not remaining:
                plan["emptied_sources"] |= source
                continue
            if not remaining.filtered("active"):
                plan["emptied_sources"] |= source
            if source.has_dynamic_attributes():
                continue
            source_configuration = self._get_template_configuration(source)
            used = defaultdict(set)
            for variant in remaining:
                for value in variant.product_template_attribute_value_ids:
                    used[value.attribute_id.id].add(value.product_attribute_value_id.id)
            removals = {
                attribute_id: values - used[attribute_id]
                for attribute_id, values in source_configuration.items()
                if used[attribute_id] and values - used[attribute_id]
            }
            plan["source_removals"][source] = removals
            final_source = {
                attribute_id: values - removals.get(attribute_id, set())
                for attribute_id, values in source_configuration.items()
            }
            excluded = self._get_excluded_value_pairs(source)
            source_combinations = {
                self._get_combination(v)
                for v in source.with_context(active_test=False).product_variant_ids
            }
            missing_before = (
                self._get_possible_combinations(source_configuration, excluded)
                - source_combinations
            )
            possible_after = self._get_possible_combinations(final_source, excluded)
            missing_after = possible_after - {
                self._get_combination(v) for v in remaining
            }
            pairs, creations = self._resolve_missing_combinations(
                possible_after, missing_after - missing_before, set()
            )
            plan["exclusions"][source] = pairs
            plan["creations"][source] = creations
            if creations:
                warnings.append(
                    _(
                        "%(origin)s keeps %(count)s combinations that cannot be "
                        "excluded; Odoo will generate them again in it.",
                        origin=source.display_name,
                        count=len(creations),
                    )
                )
        self._plan_sale_prices(plan)
        self._add_template_record_warnings(plan)
        if moved.filtered(lambda p: not p.active):
            warnings.append(
                _(
                    "Archived variants with a valid combination are reactivated "
                    "by Odoo the next time the attributes of the target change."
                )
            )
        return plan

    @api.model
    def _get_variant_price_field(self):
        """Field storing a sales price per variant, as product_variant_sale_price
        does. Moving a variant keeps it, so extra prices are not used."""
        return "fix_price" if "fix_price" in self.env["product.product"]._fields else ""

    @api.model
    def _variant_prices_are_independent(self):
        return bool(self._get_variant_price_field())

    def _snapshot_variant_prices(self, variants):
        price_field = self._get_variant_price_field()
        if not price_field or not self.keep_sale_price:
            return {}
        return {variant: variant[price_field] for variant in variants}

    def _restore_variant_prices(self, prices):
        """Modules storing a price per variant may reset it whenever the variant
        synchronization runs, which the move triggers through the core."""
        price_field = self._get_variant_price_field()
        digits = self.env["decimal.precision"].precision_get("Product Price")
        for variant, price in prices.items():
            if float_compare(variant[price_field], price, precision_digits=digits):
                variant[price_field] = price

    def _solve_price_extras(self, plan, known, free):
        """Find the extra price of each added value that keeps the sales price
        of the moved variants using it. A value is solved when every variant
        whose only unsolved value it is needs the same amount."""
        target = self.target_tmpl_id._origin
        digits = self.env["decimal.precision"].precision_get("Product Price")
        resolved = {}
        conflicting = set()
        progress = True
        while progress:
            progress = False
            needs = defaultdict(list)
            for variant, combination in plan["moves"].items():
                unknown = [v for v in combination if v in free and v not in resolved]
                if len(unknown) != 1 or unknown[0] in conflicting:
                    continue
                base = target.list_price + sum(
                    known.get(v, resolved.get(v, 0.0))
                    for v in combination
                    if v != unknown[0]
                )
                needs[unknown[0]].append(
                    float_round(variant.lst_price - base, precision_digits=digits)
                )
            for value_id, amounts in needs.items():
                if all(
                    float_compare(a, amounts[0], precision_digits=digits) == 0
                    for a in amounts
                ):
                    resolved[value_id] = amounts[0]
                    progress = True
                else:
                    conflicting.add(value_id)
        return resolved

    def _plan_sale_prices(self, plan):
        if self._variant_prices_are_independent():
            return
        target = self.target_tmpl_id._origin
        value_model = self.env["product.attribute.value"]
        configured = set().union(*plan["configuration"].values())
        extras = {}
        # Values that were removed from the target keep their old extra price
        # when Odoo reactivates them.
        previous = {}
        for value in self.env["product.template.attribute.value"].search(
            [("product_tmpl_id", "=", target.id)]
        ):
            value_id = value.product_attribute_value_id.id
            (extras if value_id in configured else previous)[value_id] = (
                value.price_extra
            )
        added = set().union(*plan["value_additions"].values())
        defaults = set(plan["defaults"].values())
        if self.keep_sale_price:
            for value_id in defaults:
                extras[value_id] = 0.0
            free = added - defaults
            extras.update(self._solve_price_extras(plan, extras, free))
        for value_id in added - set(extras):
            extras[value_id] = previous.get(
                value_id, value_model.browse(value_id).default_extra_price
            )
        if self.keep_sale_price:
            plan["price_extras"] = {v: extras[v] for v in added}
        digits = self.env["decimal.precision"].precision_get("Product Price")
        changed = []
        for variant, combination in plan["moves"].items():
            new_price = target.list_price + sum(extras.get(v, 0.0) for v in combination)
            if float_compare(variant.lst_price, new_price, precision_digits=digits):
                changed.append(
                    f"{variant.display_name}: {variant.lst_price} → {new_price}"
                )
        if changed:
            plan["warnings"].append(
                _(
                    "The sales price of these variants changes: %(variants)s",
                    variants="; ".join(changed),
                )
            )
        shifted = [
            value_model.browse(value_id)
            for value_id in defaults
            if float_compare(extras[value_id], 0.0, precision_digits=digits)
        ]
        if shifted:
            plan["warnings"].append(
                _(
                    "The sales price of the existing variants of %(target)s "
                    "changes by the extra price of %(values)s.",
                    target=target.display_name,
                    values=", ".join(v.name for v in shifted),
                )
            )

    def _add_template_record_warnings(self, plan):
        target = self.target_tmpl_id._origin
        for (
            model_name,
            tmpl_field,
            variant_field,
        ) in self._get_template_variant_fields():
            count = (
                self.env[model_name]
                .sudo()
                .with_context(active_test=False)
                .search_count(
                    [(tmpl_field, "=", target.id), (variant_field, "=", False)]
                )
            )
            if count:
                plan["warnings"].append(
                    _(
                        "%(count)s %(model)s records of %(target)s apply to all its "
                        "variants, the moved ones included.",
                        count=count,
                        model=self.env["ir.model"]._get(model_name).name,
                        target=target.display_name,
                    )
                )

    def _render_preview(self, plan):
        attribute_value = self.env["product.attribute.value"]
        items = []
        if plan["moves"]:
            items.append(
                _(
                    "Move %(count)s variants keeping their identifier.",
                    count=len(plan["moves"]),
                )
            )
        for value_ids in plan["value_additions"].values():
            values = attribute_value.browse(sorted(value_ids))
            items.append(
                _(
                    "Add %(values)s to %(attribute)s.",
                    values=", ".join(values.mapped("name")),
                    attribute=values.attribute_id.name,
                )
            )
        for value_ids in plan["no_variant_additions"].values():
            values = attribute_value.browse(sorted(value_ids))
            items.append(
                _(
                    "Add %(values)s to %(attribute)s (does not create variants).",
                    values=", ".join(values.mapped("name")),
                    attribute=values.attribute_id.name,
                )
            )
        for value_id in plan["defaults"].values():
            value = attribute_value.browse(value_id)
            items.append(
                _(
                    "Existing variants of the target get %(attribute)s: %(value)s.",
                    attribute=value.attribute_id.name,
                    value=value.name,
                )
            )
        for template, removals in plan["source_removals"].items():
            for value_ids in removals.values():
                items.append(
                    _(
                        "Remove %(values)s from %(template)s.",
                        values=", ".join(
                            attribute_value.browse(sorted(value_ids)).mapped("name")
                        ),
                        template=template.display_name,
                    )
                )
        for template, pairs in plan["exclusions"].items():
            if pairs:
                items.append(
                    _(
                        "Create %(count)s attribute exclusions in %(template)s.",
                        count=len(pairs),
                        template=template.display_name,
                    )
                )
        for template, creations in plan["creations"].items():
            if creations:
                items.append(
                    _(
                        "Create %(count)s variants in %(template)s.",
                        count=len(creations),
                        template=template.display_name,
                    )
                )
        for source in plan["emptied_sources"]:
            if self.source_template_policy == "merge":
                items.append(
                    _(
                        "Merge %(origin)s into the target, or archive it if "
                        "something prevents it.",
                        origin=source.display_name,
                    )
                )
            else:
                items.append(_("Archive %(origin)s.", origin=source.display_name))

        def section(title, entries, css):
            if not entries:
                return Markup()
            return Markup(
                '<div class="alert %s mb-2" role="alert"><strong>%s</strong>'
                '<ul class="mb-0">%s</ul></div>'
            ) % (
                css,
                title,
                Markup().join(Markup("<li>%s</li>") % escape(e) for e in entries),
            )

        return (
            section(_("Blocking problems"), plan["errors"], "alert-danger")
            + section(_("Warnings"), plan["warnings"], "alert-warning")
            + section(_("Changes"), items, "alert-info")
        )

    @api.model
    def _get_excluded_models(self):
        return {
            "product.product",
            "product.template",
            "product.template.attribute.line",
            "product.template.attribute.value",
            "product.template.attribute.exclusion",
        }

    @api.model
    def _is_plain_reference(self, field, comodel_name, types=("many2one",)):
        return (
            field.type in types
            and field.comodel_name == comodel_name
            and field.store
            and not field.compute
            and not field.related
            and not field.inherited
        )

    @api.model
    def _get_persistent_models(self):
        excluded = self._get_excluded_models()
        for model_name in self.env.registry:
            model = self.env[model_name]
            if (
                model_name in excluded
                or model._transient
                or model._abstract
                or not model._auto
            ):
                continue
            yield model

    @api.model
    @tools.ormcache()
    def _get_template_variant_fields(self):
        """Return ``(model, template field, variant field)`` for the models that
        can target either a whole template or one of its variants, like vendor
        prices or pricelist rules."""
        result = []
        for model in self._get_persistent_models():
            template_fields = [
                f
                for f in model._fields.values()
                if self._is_plain_reference(f, "product.template")
            ]
            variant_fields = [
                f
                for f in model._fields.values()
                if self._is_plain_reference(f, "product.product")
            ]
            if len(template_fields) == 1 and len(variant_fields) == 1:
                result.append(
                    (model._name, template_fields[0].name, variant_fields[0].name)
                )
        return tuple(result)

    @api.model
    def _get_specialization_values(self, model_name):
        """Extra values to write when a template-level record is narrowed to
        one variant."""
        if model_name == "product.pricelist.item":
            return {"applied_on": "0_product_variant"}
        return {}

    def _lock_records(self, templates, variants):
        try:
            with self.env.cr.savepoint(flush=False), mute_logger("odoo.sql_db"):
                self.env.cr.execute(
                    SQL(
                        "SELECT id FROM product_template WHERE id IN %s "
                        "FOR UPDATE NOWAIT",
                        tuple(templates.ids),
                    )
                )
                self.env.cr.execute(
                    SQL(
                        "SELECT id FROM product_product WHERE id IN %s "
                        "FOR UPDATE NOWAIT",
                        tuple(variants.ids),
                    )
                )
        except LockNotAvailable:
            raise UserError(
                _("Another user is modifying these products. Try again in a " "moment.")
            ) from None

    def _snapshot_variants(self, template):
        return {
            variant.id: (variant.active, self._get_combination(variant))
            for variant in template.with_context(active_test=False).product_variant_ids
        }

    def _simulate_variant_sync(self, templates):
        """Run the core variant synchronization inside a savepoint that is
        rolled back, and return what it would change for each template."""
        result = {}
        for template in templates:
            before = self._snapshot_variants(template)
            try:
                with self.env.cr.savepoint():
                    template.with_context(
                        **{SKIP_VARIANT_SYNC: False}
                    )._create_variant_ids()
                    # Overrides may write after the core flush; those writes
                    # must reach the database before the rollback, or they
                    # would be flushed afterwards and survive it.
                    self.env.flush_all()
                    raise _SimulationRollback(self._snapshot_variants(template))
            except _SimulationRollback as rollback:
                after = rollback.args[0]
            except Exception as error:  # pylint: disable=broad-except
                result[template.id] = {"error": str(error)}
                continue
            finally:
                self.env.invalidate_all(flush=False)
                self.env.registry.clear_cache()
            result[template.id] = {
                "created": {
                    combination
                    for vid, (_active, combination) in after.items()
                    if vid not in before
                },
                "removed": set(before) - set(after),
                "activated": {
                    vid
                    for vid, (active, _c) in after.items()
                    if vid in before and active and not before[vid][0]
                },
                "archived": {
                    vid
                    for vid, (active, _c) in after.items()
                    if vid in before and not active and before[vid][0]
                },
            }
        return result

    def _check_variant_sync(self, before, after, moved):
        problems = []
        for template_id, post in after.items():
            template = self.env["product.template"].browse(template_id)
            pre = before.get(template_id) or {}
            if "error" in pre:
                continue
            if "error" in post:
                problems.append(f"{template.display_name}: {post['error']}")
                continue
            created = post["created"] - pre["created"]
            removed = post["removed"] - pre["removed"]
            archived = post["archived"] - pre["archived"]
            activated = post["activated"] - pre["activated"] - set(moved.ids)
            if created or removed or archived or activated:
                problems.append(
                    _(
                        "%(template)s: Odoo would create %(created)s, delete "
                        "%(removed)s, archive %(archived)s and reactivate "
                        "%(activated)s variants.",
                        template=template.display_name,
                        created=len(created),
                        removed=len(removed),
                        archived=len(archived),
                        activated=len(activated),
                    )
                )
        if problems:
            raise UserError(
                _(
                    "The move would leave the attributes inconsistent with the "
                    "variants:\n%(problems)s",
                    problems="\n".join(problems),
                )
            )

    def _get_value_map(self, template):
        """Map attribute value ids to the active template attribute values."""
        return {
            value.product_attribute_value_id.id: value
            for value in self._get_variant_lines(
                template
            ).product_template_value_ids._only_active()
        }

    def _add_template_values(self, template, additions):
        """Add attribute values to the template, creating the lines if needed."""
        new_lines = []
        for attribute_id, value_ids in additions.items():
            line = template.attribute_line_ids.filtered(
                lambda ln, a=attribute_id: ln.attribute_id.id == a
            )
            if line:
                line.write({"value_ids": [Command.link(v) for v in sorted(value_ids)]})
            else:
                new_lines.append(
                    {
                        "product_tmpl_id": template.id,
                        "attribute_id": attribute_id,
                        "value_ids": [Command.set(sorted(value_ids))],
                    }
                )
        if new_lines:
            self.env["product.template.attribute.line"].create(new_lines)

    def _apply_target_configuration(self, plan):
        target = self.target_tmpl_id
        self._add_template_values(target, plan["value_additions"])
        self._add_template_values(target, plan["no_variant_additions"])
        if plan["price_extras"]:
            value_map = self._get_value_map(target)
            for value_id, extra in plan["price_extras"].items():
                value_map[value_id].price_extra = extra
        if plan["defaults"]:
            value_map = self._get_value_map(target)
            plan["target_existing"].write(
                {
                    "product_template_attribute_value_ids": [
                        Command.link(value_map[value_id].id)
                        for value_id in plan["defaults"].values()
                    ]
                }
            )

    def _move_variants(self, plan):
        target = self.target_tmpl_id
        value_map = self._get_value_map(target)
        for variant, combination in plan["moves"].items():
            source = variant.product_tmpl_id
            vals = {
                "product_tmpl_id": target.id,
                "product_template_attribute_value_ids": [
                    Command.set([value_map[value_id].id for value_id in combination])
                ],
            }
            if (
                not variant.image_variant_1920
                and source.image_1920
                and source.image_1920 != target.image_1920
            ):
                vals["image_variant_1920"] = source.image_1920
            variant.write(vals)
        # A later partial flush (e.g. triggered by a search) could write the new
        # template without the recomputed combination and hit the unique index.
        self.env.flush_all()

    def _specialize_template_records(self, plan, sources_by_variant):
        """Make the records of the sources follow the moved variants.

        Records already bound to a moved variant just change their template.
        Records bound to the whole source template are narrowed to each moved
        variant, so they keep applying to the same products and do not spread
        to the other variants of the target.
        """
        target = self.target_tmpl_id
        moved = self.env["product.product"].concat(*plan["moves"])
        moved_by_source = defaultdict(lambda: self.env["product.product"])
        for variant in moved:
            moved_by_source[sources_by_variant[variant.id]] |= variant
        sources = plan["sources"]
        # Consistency across models the user may not access is part of the move.
        for (
            model_name,
            tmpl_field,
            variant_field,
        ) in self._get_template_variant_fields():
            model = self.env[model_name].sudo().with_context(active_test=False)
            records = model.search([(tmpl_field, "in", sources.ids)])
            if not records:
                continue
            variant_level = records.filtered(lambda r, f=variant_field: r[f] in moved)
            variant_level.write({tmpl_field: target.id})
            extra = self._get_specialization_values(model_name)
            for record in (records - variant_level).filtered(
                lambda r, f=variant_field: not r[f]
            ):
                source = record[tmpl_field]
                variants = moved_by_source[source]
                if not variants:
                    continue
                # Copies are taken before the original is reused for the last
                # variant, so they all start from the unchanged record.
                can_reuse = not source.with_context(
                    active_test=False
                ).product_variant_ids
                for variant in variants:
                    self._narrow_record_to_variant(
                        record,
                        variant,
                        dict(
                            extra, **{tmpl_field: target.id, variant_field: variant.id}
                        ),
                        plan,
                        reuse=can_reuse and variant == variants[-1],
                    )

    def _narrow_record_to_variant(self, record, variant, values, plan, reuse=False):
        """Make a template-level record of a source apply only to ``variant``.
        The record itself is reused when the source keeps no other variant it
        could apply to; otherwise a copy is made. ``plan["source_combinations"]``
        holds the attribute values the variant had in its source."""
        if reuse:
            record.write(values)
            return record
        return record.copy(values)

    def _clean_source_configuration(self, plan):
        for source, removals in plan["source_removals"].items():
            source = source.with_env(self.env)
            for attribute_id, value_ids in removals.items():
                line = source.attribute_line_ids.filtered(
                    lambda ln, a=attribute_id: ln.attribute_id.id == a
                )
                line.write({"value_ids": [Command.unlink(v) for v in value_ids]})

    def _apply_missing_combinations(self, plan):
        exclusion_model = self.env["product.template.attribute.exclusion"]
        for template, pairs in plan["exclusions"].items():
            if not pairs:
                continue
            value_map = self._get_value_map(template)
            excluded = defaultdict(set)
            for pair in pairs:
                first, second = sorted(pair)
                excluded[first].add(second)
            exclusion_model.create(
                [
                    {
                        "product_tmpl_id": template.id,
                        "product_template_attribute_value_id": value_map[first].id,
                        "value_ids": [
                            Command.set([value_map[v].id for v in sorted(others)])
                        ],
                    }
                    for first, others in excluded.items()
                ]
            )
        for template, creations in plan["creations"].items():
            if not creations:
                continue
            value_map = self._get_value_map(template)
            self.env["product.product"].create(
                [
                    template._prepare_variant_values(
                        self.env["product.template.attribute.value"].concat(
                            *[value_map[v] for v in sorted(combination)]
                        )
                    )
                    for combination in creations
                ]
            )

    def _remap_attribute_value_references(self, source):
        """Point the records using template attribute values of the source,
        like the non-variant values of sales order lines, to the equivalent
        values of the target so deleting the source loses nothing."""
        value_model = self.env["product.template.attribute.value"]
        source_values = value_model.search([("product_tmpl_id", "=", source.id)])
        if not source_values:
            return
        target_values = {}
        for value in value_model.search(
            [("product_tmpl_id", "=", self.target_tmpl_id.id)],
            order="ptav_active desc, id",
        ):
            target_values.setdefault(value.product_attribute_value_id.id, value)
        for model in self._get_persistent_models():
            for field in model._fields.values():
                if not (
                    field.type in ("many2one", "many2many")
                    and field.comodel_name == "product.template.attribute.value"
                    and field.store
                    and not field.related
                ):
                    continue
                records = (
                    model.sudo()
                    .with_context(active_test=False)
                    .search([(field.name, "in", source_values.ids)])
                )
                groups = defaultdict(model.sudo().browse)
                for record in records:
                    groups[record[field.name] & source_values] |= record
                for old_values, group in groups.items():
                    new_values = value_model
                    for old in old_values:
                        new = target_values.get(old.product_attribute_value_id.id)
                        if not new:
                            raise _MergeAbort(
                                _(
                                    "%(value)s is used by %(model)s and has no "
                                    "equivalent in the target.",
                                    value=old.display_name,
                                    model=model._description,
                                )
                            )
                        new_values |= new
                    if field.type == "many2one":
                        group.write({field.name: new_values.id})
                    else:
                        group.write(
                            {
                                field.name: [Command.unlink(v.id) for v in old_values]
                                + [Command.link(v.id) for v in new_values]
                            }
                        )

    def _remap_template_references(self, source):
        target = self.target_tmpl_id
        template_model = self.env["product.template"]
        owned_relations = {
            f.relation for f in template_model._fields.values() if f.type == "many2many"
        }
        for field in template_model._fields.values():
            if self._is_plain_reference(field, "product.template", ("many2many",)):
                referencing = (
                    template_model.sudo()
                    .with_context(active_test=False)
                    .search([(field.name, "in", source.ids), ("id", "!=", source.id)])
                )
                commands = [Command.unlink(source.id)]
                (referencing - target).write(
                    {field.name: commands + [Command.link(target.id)]}
                )
                (referencing & target).write({field.name: commands})
        for model in self._get_persistent_models():
            for field in model._fields.values():
                if self._is_plain_reference(field, "product.template"):
                    model.sudo().with_context(active_test=False).search(
                        [(field.name, "=", source.id)]
                    ).write({field.name: target.id})
                elif (
                    self._is_plain_reference(field, "product.template", ("many2many",))
                    and field.relation not in owned_relations
                ):
                    model.sudo().with_context(active_test=False).search(
                        [(field.name, "in", source.ids)]
                    ).write(
                        {
                            field.name: [
                                Command.unlink(source.id),
                                Command.link(target.id),
                            ]
                        }
                    )
                elif field.type == "many2one_reference" and field.store:
                    self._remap_generic_references(model, field, source)
                elif (
                    field.type == "reference"
                    and field.store
                    and not field.compute
                    and not field.related
                ):
                    model.sudo().with_context(active_test=False).search(
                        [(field.name, "=", f"product.template,{source.id}")]
                    ).write({field.name: f"product.template,{target.id}"})

    def _remap_generic_references(self, model, field, source):
        target = self.target_tmpl_id
        records = (
            model.sudo()
            .with_context(active_test=False)
            .search(
                [
                    (field.model_field, "=", "product.template"),
                    (field.name, "=", source.id),
                ]
            )
        )
        if not records:
            return
        if model._name == "ir.model.data":
            owned = records.filtered(lambda r: not r.module.startswith("__"))
            if owned:
                raise _MergeAbort(
                    _(
                        "It is defined by the module data %(xmlids)s.",
                        xmlids=", ".join(owned.mapped("complete_name")),
                    )
                )
        elif model._name == "mail.followers":
            duplicated = records.filtered(
                lambda r: r.partner_id in target.message_partner_ids
            )
            duplicated.unlink()
            records -= duplicated
        records.write({field.name: target.id})

    def _merge_template(self, source):
        """Try to merge an emptied source into the target. Return the reason
        why it was not possible, if any."""
        try:
            with self.env.cr.savepoint(), mute_logger("odoo.sql_db"):
                self._remap_attribute_value_references(source)
                self._remap_template_references(source)
                source.sudo().unlink()
                self.env.flush_all()
        except _MergeAbort as error:
            return str(error)
        except Exception as error:  # pylint: disable=broad-except
            return str(error)
        finally:
            # Pending writes of an aborted merge must not outlive its rollback.
            self.env.invalidate_all(flush=False)
        return False

    def _prepare_source_removal(self, source):
        """Hook called before an emptied source is archived or merged."""

    def _process_emptied_sources(self, plan):
        """Return ``(merged templates' names, {archived template: reason})``."""
        merged = []
        archived = {}
        for source in plan["emptied_sources"]:
            self._prepare_source_removal(source)
            reason = False
            if self.source_template_policy == "merge":
                if source.with_context(active_test=False).product_variant_ids:
                    reason = _("It keeps archived variants.")
                else:
                    name = source.display_name
                    reason = self._merge_template(source)
                    if not reason:
                        merged.append(name)
                        continue
            source.active = False
            archived[source] = reason
        return merged, archived

    def _post_messages(self, plan, merged, archived):
        target = self.target_tmpl_id
        variants = Markup().join(
            Markup(
                '<li><a href="#" data-oe-model="product.product" '
                'data-oe-id="%s">%s</a></li>'
            )
            % (variant.id, variant.display_name)
            for variant in plan["moves"]
        )
        body = Markup("<p>%s</p><ul>%s</ul>") % (
            _("Variants moved to this template:"),
            variants,
        )
        if merged:
            body += Markup("<p>%s</p>") % _(
                "Merged templates: %(names)s", names=", ".join(merged)
            )
        for source, reason in archived.items():
            text = _("Archived template: %(name)s", name=source.display_name)
            if reason:
                text = _("%(text)s (not merged: %(reason)s)", text=text, reason=reason)
            body += Markup("<p>%s</p>") % text
        target.message_post(body=body)
        for source in plan["sources"].exists():
            source.message_post(
                body=Markup(
                    '<p>%s <a href="#" data-oe-model="product.template" '
                    'data-oe-id="%s">%s</a></p>'
                )
                % (_("Variants moved to"), target.id, target.display_name)
            )

    def action_move(self):
        self.ensure_one()
        self.env["product.template"].check_access("write")
        self.env["product.product"].check_access("write")
        plan = self._prepare_plan()
        if plan["errors"]:
            raise UserError("\n".join(plan["errors"]))
        target = self.target_tmpl_id
        moved = self.env["product.product"].concat(*plan["moves"])
        sources_by_variant = {v.id: v.product_tmpl_id for v in moved}
        with self.env.cr.savepoint():
            self._lock_records(target | plan["sources"], moved)
            checked = target | plan["sources"].filtered(
                lambda s, m=moved: s.with_context(active_test=False).product_variant_ids
                - m
            )
            before = self._simulate_variant_sync(checked)
            prices = self._snapshot_variant_prices(
                (moved | plan["target_existing"] | plan["sources"].product_variant_ids)
                .with_context(active_test=False)
                .exists()
            )
            wizard = self.with_context(**{SKIP_VARIANT_SYNC: True})
            wizard._apply_target_configuration(plan)
            wizard._move_variants(plan)
            wizard._specialize_template_records(plan, sources_by_variant)
            wizard._clean_source_configuration(plan)
            wizard._apply_missing_combinations(plan)
            self._restore_variant_prices(prices)
            self.env.flush_all()
            after = self._simulate_variant_sync(checked)
            self._check_variant_sync(before, after, moved)
            merged, archived = self._process_emptied_sources(plan)
            self._post_messages(plan, merged, archived)
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "res_id": target.id,
            "view_mode": "form",
            "target": "current",
        }


class ProductVariantChangeTemplateLine(models.TransientModel):
    _name = "product.variant.change.template.line"
    _description = "Variant to move to another template"

    wizard_id = fields.Many2one(
        comodel_name="product.variant.change.template",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Variant",
        required=True,
        ondelete="cascade",
        context={"active_test": False},
    )
    source_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id", string="Current Template"
    )
    source_combination = fields.Char(
        string="Current Attributes", compute="_compute_source_combination"
    )
    value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="product_variant_change_template_line_value_rel",
        string="Attributes in the Target",
        domain=[("attribute_id.create_variant", "!=", "no_variant")],
    )

    @api.depends("product_id")
    def _compute_source_combination(self):
        for line in self:
            line.source_combination = ", ".join(
                line.product_id.product_template_attribute_value_ids.mapped(
                    "display_name"
                )
            )


class ProductVariantChangeTemplateAttribute(models.TransientModel):
    _name = "product.variant.change.template.attribute"
    _description = "Value of a new attribute for the existing target variants"

    wizard_id = fields.Many2one(
        comodel_name="product.variant.change.template",
        required=True,
        ondelete="cascade",
    )
    attribute_id = fields.Many2one(
        comodel_name="product.attribute", required=True, ondelete="cascade"
    )
    value_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Value",
        domain="[('attribute_id', '=', attribute_id)]",
        ondelete="cascade",
    )
