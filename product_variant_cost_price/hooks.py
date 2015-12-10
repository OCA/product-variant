# -*- coding: utf-8 -*-
# © 2015 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, SUPERUSER_ID


def load_cost_price_on_variant(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        for field_name in ('standard_price', 'cost_method'):
            template_field = env['ir.model.fields'].search(
                [('model', '=', 'product.template'),
                 ('name', '=', field_name)])
            product_field = env['ir.model.fields'].search(
                [('model', '=', 'product.product'),
                 ('name', '=', field_name)])
            cr.execute("""
                SELECT
                    NULLIF(substring(ir_property.res_id from 17), '')::
                        integer
                FROM
                    ir_property
                WHERE
                    ir_property.fields_id = %s
            """, (product_field.id, ))
            existing_ids = [x[0] for x in cr.fetchall()]
            sql = """
                INSERT INTO ir_property
                    (name, type, value_text, value_float, value_integer,
                    company_id, res_id, fields_id)
                SELECT
                    %s,
                    ir_property.type,
                    ir_property.value_text,
                    ir_property.value_float,
                    ir_property.value_integer,
                    ir_property.company_id,
                    'product.product,' || product_product.id::text,
                    %s
                FROM
                    ir_property,
                    product_product
                WHERE
                    ir_property.fields_id = %s
                AND
                    NULLIF(substring(ir_property.res_id from 18), '')::
                        integer = product_product.product_tmpl_id
            """
            if existing_ids:
                cr.execute(
                    sql + "AND product_product.id NOT IN %s",
                    (field_name, product_field.id, template_field.id,
                     tuple(existing_ids)))
            else:
                cr.execute(
                    sql, (field_name, product_field.id, template_field.id))
