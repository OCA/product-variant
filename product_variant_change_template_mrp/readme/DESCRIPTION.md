Bills of materials support for *Product Variant Change Template*.

- A bill of materials of a source template is narrowed to each moved variant:
  a copy is made for the variant, keeping only the components, operations and
  by-products that applied to it and clearing their *Apply on Variants*
  restriction. When the source template keeps no other variant, the original
  bill of materials is archived. Existing bills of materials are never
  rewritten, because stock moves of manufacturing orders and kits point to
  their lines.
- When a source template keeps other variants and loses attribute values, its
  bills of materials are replaced by a version without the elements that only
  applied to the removed values. Otherwise those elements would lose their
  restriction and start applying to every remaining variant.
- Elements restricted by attributes that do not create variants cannot be
  expressed in the bill of materials of a single variant, so the move is
  refused with an explanation.
