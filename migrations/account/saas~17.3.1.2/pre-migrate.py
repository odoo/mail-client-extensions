from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_translatable(cr, "account.tax.group", "preceding_subtotal")
    cr.execute("DROP INDEX IF EXISTS account_bank_statement_line_internal_index_move_id_amount_idx")
    cr.execute("""
        DELETE
          FROM ir_sequence s
         USING account_journal j
         WHERE s.id = j.secure_sequence_id
    """)
    util.remove_field(cr, "account.journal", "secure_sequence_id")
    util.remove_field(cr, "account.move", "string_to_hash")
    util.remove_field(cr, "account.group", "parent_path")
    util.change_field_selection_values(cr, "account.report.expression", "date_scope", {"normal": "strict_range"})

    util.remove_record(cr, "account.action_open_sale_payment_items")
    util.rename_xmlid(cr, "account.action_open_payment_items", "account.action_amounts_to_settle")

    util.remove_model(cr, "account.tour.upload.bill")
    util.remove_model(cr, "account.tour.upload.bill.email.confirm")
    util.remove_record(cr, "account.menu_account_supplier_accounts")
    util.remove_record(cr, "account.onboarding_onboarding_step_create_invoice")
    util.remove_record(cr, "account.onboarding_onboarding_step_bank_account")
    util.remove_record(cr, "account.onboarding_onboarding_step_default_taxes")
    util.remove_record(cr, "account.onboarding_onboarding_step_setup_bill")
    util.remove_record(cr, "account.onboarding_onboarding_account_invoice")
