from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_reconcile_model", "journal_id", "integer")
    cr.execute("""
        WITH subquery AS (
            SELECT arml.model_id,
                   MIN(arml.journal_id) AS journal_id
              FROM account_reconcile_model_line arml
              JOIN account_reconcile_model arm
                ON arm.id = arml.model_id
              JOIN account_journal aj
                ON aj.id = arml.journal_id
             WHERE arm.counterpart_type = aj.type
               AND arm.counterpart_type != 'general'
             GROUP BY arml.model_id
        )
        UPDATE account_reconcile_model arm
           SET journal_id = subquery.journal_id
          FROM subquery
         WHERE arm.id = subquery.model_id
    """)
    util.remove_column(cr, "account_reconcile_model_line", "journal_id")

    util.remove_field(cr, "account.journal", "account_control_ids")
    util.remove_field(cr, "account.reconcile.model", "match_nature")
    util.remove_field(cr, "account.reconcile.model", "match_transaction_type")
    util.remove_field(cr, "account.reconcile.model", "match_transaction_type_param")
    util.remove_field(cr, "account.reconcile.model.line", "show_force_tax_included")
    util.remove_field(cr, "account.reconcile.model.line", "force_tax_included")

    util.remove_view(cr, "account.view_account_reconcile_model_line_form")
    util.remove_view(cr, "account.product_template_view_tree")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "account.account_banks_menu"),
            util.ref(cr, "account.menu_action_account_bank_journal_form"),
            util.ref(cr, "account.menu_action_account_credit_card_journal_form"),
            util.ref(cr, "account.action_account_reconcile_model_menu"),
            util.ref(cr, "account.account_management_menu"),
        ],
    )

    cr.execute("""
      UPDATE ir_sequence
         SET prefix = 'GROUP/%(year)s/'
        FROM res_company c
       WHERE ir_sequence.prefix = 'BATCH/%(year)s/'
         AND c.batch_payment_sequence_id = ir_sequence.id
    """)

    util.create_column(cr, "account_move_line", "deductible_amount", "float8", default=100.00)
    util.remove_view(cr, "account.portal_my_details_fields")
