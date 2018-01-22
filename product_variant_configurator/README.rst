.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
Product Variant Configurator
============================

Provides an abstract model for product variant configuration. It provides the
basic functionality for presenting a table with the attributes of a template
and the possibility to select one of the valid values. You can try this
functionality creating a product variant directly selecting a product
template that has attributes.

This module also prevents in a configurable way the creation of the product
variants when defining the attributes and attribute values of the product
template.

Configuration
=============

(after installing `sale_management` application)

To configure the creation of the variants behaviour, you need to:

#. Go to ``Sales > Configuration > Settings``, and select "Attributes and
   Variants (Set product attributes (e.g. color, size) to sell variants)" on
   "Product Catalog" section.
#. Go to ``Sales > Catalog > Products``, and select a product.
#. On the Variants tab edit the value of the field ``Variant Creation``.
#. If you want to stop the automatic creation of the variant, and have the same
   behaviour for all the products in the same category, go to ``Inventory >
   Configuration > Product Categories``, select the category and check the checkbox
   ``Don't create variants automatically``.

Usage
=====

(after installing `sale_management` application)

#. Go to ``Sales > Catalog > Product Variants``.
#. Click on "Create" button for creating a new one.
#. On the field "Product Template", select a product template that has several
   attributes.
#. A table with the attributes of the template will appear below.
#. Select all the attribute values and click on "Save" button.
#. A new product variant will be created for that attributes.
#. An error will raise if there's another variant with the same attribute
   values or if you haven't filled all the required values.

Developers
----------

To use product configurator in your model, you need to:

#. The product.configurator is an abstract model, hence, to be used it must be
   inherited in your model:
#. If the model you're inheriting has ``name`` attribute, and it uses the
   related parameter you must override it.

::

    class AModel(models.Model):
        _inherit = ['module.model', 'product.configurator']
        name = fields.Char(related="delegated_field.related_field")


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/137/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/product-variant/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <ajuaristio@gmail.com>
* Thomas Binsfeld <thomas.binsfeld@acsone.eu>
* Zakaria Makrelouf (acsone) <z.makrelouf@gmail.com>
* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Laurent Mignon <laurent.mignon@acsone.eu>
* David Vidal <david.vidal@tecnativa.com>
* Simone Versienti <s.versienti@apuliasoftware.it>

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
