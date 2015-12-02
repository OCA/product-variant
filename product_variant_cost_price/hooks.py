# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def load_cost_price_on_variant(cr, registry):
    cr.execute("""
        INSERT INTO ir_property
            (name, type, value_text, value_float, value_integer, company_id,
             res_id, fields_id)
        SELECT
            ir_property.name,
            ir_property.type,
            ir_property.value_text,
            ir_property.value_float,
            ir_property.value_integer,
            ir_property.company_id,
            'product.product,' || product_product.id::text,
            ir_model_fields.id
        FROM
            ir_property,
            product_product,
            ir_model_fields
        WHERE
            ir_property.name IN ('standard_price', 'cost_method')
        AND
            NULLIF(substring(ir_property.res_id from 18), '')::integer =
                product_product.product_tmpl_id
        AND
            ir_model_fields.model = 'product.product'
        AND
            ir_model_fields.name = ir_property.name
        ;
    """)
