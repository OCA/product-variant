.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Product Variant Configurator
============================

Provides an abstract model for product variant configuration.

Installation
============

To install this module, you need to:

#. Add this module to your addons path.
#. Restart your odoo server.
#. As Admin user, update the module list by going to: ``Settings > Update Modules List``.
#. Search for your module and click install.

Configuration
=============

To configure the creation of the variants behaviour, you need to:

#. Go to ``Warehouse > Products``, and select a product.
#. on the Variants tab edit the value of the field ``Variant Creation``.
#. If you want to stop the automatic creation of the variant, and have the same behaviour for all the products in the same category, go to ``Warehouse > Products > Product Categories``, select the category and check the checkbox ``Don't create variants automatically``.

Usage
=====

For developer to use product configurator in your model, you need to:

#. The product.configurator is an abstract model, hence, to be used it must be inherited in your model:
#. If the model you're inheriting has ``name`` attribute, and it uses the related parameter you must override it.

::

    class AModel(models.Model):
        _inherit = ['module.model', 'product.configurator']
        name = fields.Char(related="delegated_field.related_field")


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/137/8.0

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <ajuaristio@gmail.com>
* Thomas Binsfeld <thomas.binsfeld@acsone.eu>
* Zakaria Makrelouf (acsone) <z.makrelouf@gmail.com>

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
