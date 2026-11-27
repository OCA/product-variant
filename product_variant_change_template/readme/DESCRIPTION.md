Move existing product variants to another product template, turning
independent products (for example "T-shirt M" and "T-shirt L") into variants
of a single template, or regrouping variants between templates.

The variants keep their database identifier, so none of their history
(stock moves, quants, valuation, sales, purchases, invoices, lots) is
rewritten. Only the variant itself and the configuration records bound to its
template change.

The move takes care of:

- Adding the attribute values, or whole attributes, the moved variants need
  to the target template. When a new attribute is added, the existing target
  variants receive the value you choose for it.
- Keeping the attribute configuration consistent with the variants: the
  combinations that become possible but no variant uses are excluded with
  attribute exclusions (or created, if you prefer), so Odoo does not generate
  or delete variants the next time the attributes change. Before committing,
  the result is checked by running the standard variant synchronization in a
  rolled back savepoint.
- Cleaning the source templates that keep other variants: values no longer
  used are removed and the combinations left empty are excluded.
- Vendor prices, pricelist rules and any other record that can target either
  a template or one of its variants: records of the moved variants follow
  them, and records of the whole source template are narrowed to each moved
  variant, so they do not start applying to the other target variants.
- Keeping sales prices: the extra price of the attribute values added to the
  target is set so each moved variant keeps its sales price whenever the
  variants using a value need the same amount, and a new attribute does not
  change the price of the existing target variants. The variants whose price
  still changes are listed before confirming. With *Product Variant Sale
  Price* installed, each variant keeps its own price and nothing is adjusted.
- Copying the attributes that do not create variants.
- Archiving the source templates left without variants, or merging them into
  the target: chatter, attachments, imported external identifiers, links from
  other records (including reference fields such as the record of a server
  action) and non-variant attribute values used in documents are repointed to
  the target before deleting the source. When something prevents
  it (for example the template is defined by a module) the source is archived
  instead and the reason is logged.

The move is refused when the source and target templates differ in type, unit
of measure, company, storable flag, tracking or category costing method and
valuation, because the history of the moved variants would become
inconsistent. Other differences (category, taxes, routes, sales price...) are
shown as warnings before confirming.

Bills of materials are handled by *Product Variant Change Template -
Manufacturing* and shop page redirections by *Product Variant Change Template -
eCommerce*, both installed automatically with their dependencies.
