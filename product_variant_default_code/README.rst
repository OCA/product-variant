.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
Product Variant Default Code
============================

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

Configuration
=============

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

Aditionally, a product attribute can be set and so it will be appended to the
product `default_code`. In the first example, setting a `Color` code to `CO`
would give `default_code` like this: `COBl-L`, `COWh-L`, `COBl-XL` and
`COWh-XL`.

Avoiding mask in variants
-------------------------

You can avoid this behavior or force a manual default_code on variant. To do
so, go to *Product Variants > [any variant you want to set up]* and set
manually its reference code. The field `manual code` will be set to on and the
variant internal reference will no longer be changed by this module.

Unset `manual code` and the reference code will be unlocked again.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/137/10.0


Known issues / Roadmap
======================

In case of attribute name update, related mask are not updated.

  
Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/product_variant/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Alfredo de la Fuente <alfredodelafuente@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Tony Gu <tony@openerp.cn>
* David Vidal <david.vidal@tecnativa.com>
* David Beal <david.beal@akretion.com>
* Daniel Campos <danielcampos@avanzosc.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
