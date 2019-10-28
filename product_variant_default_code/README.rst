.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
Product Variant Default Code
============================

This module automatically generate *Internal Reference* (`default_code`)
according to attributes, with a configurable behavior.

It defines a reference mask on the product templates, based on some 
attributes code you set before. Then variants internal references are 
automatically set. For example:

Creating a product named "Jacket" with two attributes, 'Size' and 'Color'::

   Product: Jacket
   Color:   Black(Bl), White(Wh) # Black and White are the attribute values
                                 # 'Bl' and 'Wh' are the corresponding codes
   Size:    M (M), L (L)
   
The automatically generated default value for the variant reference mask 
will be `[Color]-[Size]` and so the *Internal Reference* on the variants 
will contain::

   'Bl-M', 'Wh-M', 'Bl-L' and 'Wh-L'.

Configuration
=============

Of course, activate *Attributes and Variants* under **Sales / Product Catalogue** 
settings (or **Inventory / Products**).

Fill *Attributes Value Code* to each attribute's value.

Usage
=====

When creating a new product template, once you have added attributes and values, 
fill the new *Reference Prefix* field that appear under *Internal Reference*.

A default value for *Variant reference mask* will be automatically generated 
according to the attribute line settings on the product template. This mask will 
then be used as an instruction to generate *Internal Reference* of each product 
variant with the corresponding *Attribute Value Code* inserted. For example::

   - Product template: Jacket
   - Reference prefix: JKT
   - Attributes:
     - Color: Black, White,
     - Size: M, L
   - Reference mask:  `JKT01-[Color]-[Size]`
   - Variants Internal Reference:
     - 'JKT01-Bl-M'
     - 'JKT01-Wh-M'
     - 'JKT01-Bl-L'
     - 'JKT01-Wh-L'

Additionally, an *Attribute Code* can be set. It will be appended to the
variant *Internal Reference*. In the first example, setting a 'Color' code 
to "CO" would give *Internal Reference* (`default_code`) like this::
  'JKT01-COBl-M', 'JKT01-COWh-M', 'JKT01-COBl-L' and 'JKT01-COWh-L'.

When an attribute or value code is changed, the reference on all variants 
affected is regenerated.

Advanced
========

To manualy define the reference mask on each product, switch *Product Default 
Code* behaviour to "Manual Mask" in **General Settings**. Then, fill the 
"Variant Reference Mask" field on any product template.

The mask value can be fully customized whatever you like. You can even have
the attribute name appear more than once in the mask such as,
`Jacket/[Size]~[Color]~[Size]`, and the generated code on variants will be
something like 'Jacket/L~Wh~L' (for variant with Color "White" and Size "L").

**Note:** In mask value, make sure putting the *Attribute Name* inside `[ ]` 
marks (it is case sensitive) and of course, make sure characters "[,]" 
do not appear in your attribute's name.

Avoiding mask in variants
-------------------------

You can avoid this behavior or force a manual reference on variant. To do
so, go to **Product Variants > [any variant you want to set up]** and set
manually its reference code. The field *Manual Reference* (`manual_code`) 
will be set to on and the variant internal reference will no longer be 
changed by this module.

Unset *Manual Reference* on a variant and the reference code will be 
unlocked again.

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
