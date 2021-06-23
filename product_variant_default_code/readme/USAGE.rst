To set the reference mask up on any product template 'Variant reference mask'
new field.

When creating a new product template without specifying the *Variant reference
mask*, a default value for *Variant reference mask* will be automatically
generated according to the attribute line settings on the product template (if
any). The mask will then be used as an instruction to generate default code of
each product variant of the product template with the corresponding *Attribute
Code* (of the attribute value) inserted. Besides the default value, *Variant
reference mask* can be configured to your liking, make sure putting the
*Attribute Name* inside `[]` marks (it is case sensitive).

Example:

Creating a product named *Jacket* with two attributes, *Size* and *Color*::

   Product: Jacket
   Color: Black(Bl), White(Wh) # Black and White are the attribute values;
                                 'Bl' and 'Wh' are the corresponding codes
   Size: L (L), XL(XL)

The automatically generated default value for the Variant reference mask will
be `[Color]-[Size]` and so the 'default code' on the variants will be `Bl-L`,
`Wh-L`, `Bl-XL` and `Wh-XL`.

The mask value can be fully customized whatever you like. You can even have
the attribute name appear more than once in the mask such as,
`Jacket/[Size]~[Color]~[Size]`, and the generated code on variants will be
something like `Jacket/L~Bl~L` (for variant with Color "Black" and Size "L").

When the code attribute is changed, it automatically regenerates the 'default
code' on all variants affected.

Aditionally, a product attribute can be set and so it will be prepended to the
product `default_code`. In the first example, setting a `Color` code to `CO`
would give `default_code` like this: `COBl-L`, `COWh-L`, `COBl-XL` and
`COWh-XL`.

Avoiding mask in variants
~~~~~~~~~~~~~~~~~~~~~~~~~

You can avoid this behavior or force a manual default_code on variant. To do
so, go to *Product Variants > [any variant you want to set up]* and set
manually its reference code. The field `manual code` will be set to on and the
variant internal reference will no longer be changed by this module.

Unset `manual code` and the reference code will be unlocked again.
