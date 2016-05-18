.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Product Variant Cost
====================

This module allows to handle cost method and price at product variant level
(product.product) instead at product level (product.template), which is the
default.

Configuration
=============

For using different cost methods, you have to install *purchase* module and go
to Configuration > Purchases to enable "Use 'Real Price' or 'Average'
costing methods.", but that's an optional choice.

Usage
=====

If you go to Sales > Products > Product Variants, the cost price in the tab
"Procurements" will be changed only for that variant. If there's only one
variant, the price will be also applied to the template.

On the other hand, a change in the cost price for the template will modify
all the variants involved.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/137/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/product-variant/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/product-variant/issues/new?body=module:%
product_variant_cost_price%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Ainara Galdona <ainaragaldona@avanzosc.es>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Javier Iniesta <javieria@antiun.com>

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

