(after installing sale_management application)

1.  Go to `Sales > Products > Product Variants`.
2.  Click on "New" button for creating a new one.
3.  On the field "Product Template", select a product template that has
    several attributes.
4.  A table with the attributes of the template will appear below.
5.  Select all the attribute values and click on "Save" button.
6.  A new product variant will be created for that attributes.
7.  An error will raise if there's another variant with the same
    attribute values or if you haven't filled all the required values.

**Developers**

To use product configurator in your model, you need to:

1.  The product.configurator is an abstract model, hence, to be used it
    must be inherited in your model:
2.  If the model you're inheriting has `name` attribute, and it uses the
    related parameter you must override it.

&nbsp;

    class AModel(models.Model):
        _inherit = ['module.model', 'product.configurator']
        name = fields.Char(related="delegated_field.related_field")
