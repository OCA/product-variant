Allows to archive a `product.attribute.value` which is referenced by archived `product.product`.

In std odoo, removing a `product.attribute.value` from a `product.template`
either leads to a `product.product` unlink or archive,
depending on if the variant is referenced on a `sale.order.line` or not.
Then, if user tries to remove the `product.attribute.value` from the `product.attribute`,
he will get an error because of the `ondelete restrict` on `product.product`.
