This module automatically generate Product Reference (default_code)
according to attributes data with a configurable behavior.

It defines a reference mask on the product templates so the
variants references are automatically set. For example:

- Product template: Jacket
- Attributes:
  - Color: White, Black
  - Size: M, L
- Reference mask: `JKT01-[Color]-[Size]`

- Reference on variants:

  - `JKT01-Wh-M` Jacket White M
  - `JKT01-Bl-M` Jacket Black M
  - `JKT01-Wh-L` Jacket White L
  - `JKT01-Bl-L` Jacket Black L
