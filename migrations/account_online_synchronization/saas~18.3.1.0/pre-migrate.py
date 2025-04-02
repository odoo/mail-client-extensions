from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(
        cr, "account_bank_statement_line_transient", "transaction_details", "jsonb", using="{0}::jsonb"
    )
    util.replace_record_references(
        cr,
        ("mail.activity.type", util.ref(cr, "account_online_synchronization.bank_sync_activity_update_consent")),
        ("mail.activity.type", util.ref(cr, "mail.mail_activity_data_todo")),
        replace_xmlid=False,
    )
    util.delete_unused(cr, "account_online_synchronization.bank_sync_activity_update_consent")
