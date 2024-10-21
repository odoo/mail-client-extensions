from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "partner_credit")
    util.create_column(cr, "res_company", "income_account_id", "int4")
    cr.execute("""
        UPDATE res_company rc
           SET income_account_id = d.json_value::int4
          FROM ir_default d
          JOIN ir_model_fields imf
            ON d.field_id = imf.id
           AND imf.name = 'property_account_income_categ_id'
           AND imf.model = 'product.category'
         WHERE rc.id = d.company_id
    """)
    util.create_column(cr, "res_company", "expense_account_id", "int4")
    cr.execute("""
        UPDATE res_company rc
           SET expense_account_id = d.json_value::int4
          FROM ir_default d
          JOIN ir_model_fields imf
            ON d.field_id = imf.id
           AND imf.name = 'property_account_expense_categ_id'
           AND imf.model = 'product.category'
         WHERE rc.id = d.company_id
    """)
    util.change_field_selection_values(cr, "account.report", "filter_multi_company", {"disabled": "selector"})
