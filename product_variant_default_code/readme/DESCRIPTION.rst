This module automatically generate Product Reference (default_code)
according to attributes data with a configurable behavior.

It defines a reference mask on the product templates so the
variants references are automatically set. For example:

- Product template: Jacket
- Attributes:
  - Color(C): White(Wh), Black(Bl)
  - Size(S): M(M), L(L)
- Reference mask: `JKT01-[Color]-[Size]`

- Reference on variants:

  - `JKT01-CWh-SM` Jacket White M
  - `JKT01-CBl-SM` Jacket Black M
  - `JKT01-CWh-SL` Jacket White L
  - `JKT01-CBl-SL` Jacket Black L
