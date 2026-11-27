This module allows to mark an attribute value as unavailable, for instance
when an ingredient is out of stock. Every combination containing this value
becomes impossible, on all products using it. It applies to attributes
creating variants as well as to attributes that do not create variants.

This module does nothing visible on its own: install the module of each sales
channel, such as `pos_product_attribute_value_availability` for the Point of
Sale.
