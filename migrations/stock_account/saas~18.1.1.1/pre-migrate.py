from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "stock_valuation_layer", "categ_id")
    util.create_column(cr, "res_company", "cost_method", "text")
    cr.execute("""
        UPDATE res_company rc
           SET cost_method = d.json_value::jsonb->>0
          FROM ir_default d
          JOIN ir_model_fields imf
            ON d.field_id = imf.id
           AND imf.name = 'property_cost_method'
           AND imf.model = 'product.category'
         WHERE rc.id = d.company_id
    """)
    cr.execute("""
        UPDATE res_company rc
           SET cost_method = d.json_value::jsonb->>0
          FROM ir_default d
          JOIN ir_model_fields imf
            ON d.field_id = imf.id
           AND imf.name = 'property_cost_method'
           AND imf.model = 'product.category'
         WHERE d.company_id IS NULL
           AND rc.cost_method IS NULL
    """)
