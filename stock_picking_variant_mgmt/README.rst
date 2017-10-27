.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl.html
   :alt: License: AGPL-3

=================================================
Handle easily multiple variants on Stock Pickings
=================================================

This module allows to add/modify of all the variants of a product in a direct
screen without the need of handling them one by one.

It also adds a convenient way of handling the transfer of the products in a
2D matrix with all the values of the first attribute in columns, and the
rest of the combinations in rows.

Configuration
=============

#. Configure your user to have any permission from "Inventory" group.
#. Create a product with 2 attributes and several values.

Usage
=====

#. Go to Inventory > Dashboard.
#. Create a new picking from one of the existing picking types.
#. Press "Add variants" button located in the upper right corner of the
   "Initial Demand" tab.
#. A new screen will appear allowing you to select the products that have
   variants.
#. Once you select the product, a 2D matrix will appear with the first
   attribute values as columns and the second one (if any) as rows.
#. If there are already order lines for the product variants, the current
   quantity will be pre-filled in the matrix.
#. Change the quantities for the variant you want and click on "Transfer to
   picking"
#. Move lines for the variants will be created/removed to comply with the
   input you have done.

As extra feature for saving steps, there's also a button on each existing line
that corresponds to a variant that opens the dialog directly with the product
selected.

You are also able to manage variants on 1 dimension in the transfer:

#. Go to the "Operations" page.
#. Press on "Manage Variants Transfer" button in the upper right corner of the
   tab.
#. Change the quantities to transfer.
#. Click on "Transfer to picking" button.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/137/10.0

Known issues / Roadmap
======================

* The inline button for modifying quantities for an existing line won't
  work correctly until these 2 PRs are merged in Odoo:

  * https://github.com/odoo/odoo/pull/13557
  * https://github.com/odoo/odoo/pull/13635

  The patches are already integrated on OCB.

* On "Operations" page, only products with one attribute are shown in the 
  variant management dialog.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@tecnativa.com>

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
