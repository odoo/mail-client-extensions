from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "send_mail_warning_message")
    util.remove_field(cr, "account.move.send", "sequence_gap_warning")
    util.rename_field(cr, "mail.message", "show_audit_log", "account_audit_log_activated")
    util.remove_view(cr, "account.res_config_settings_view_form_inherit_account_audit_trail")
    util.remove_view(cr, "account.view_account_payment_method_line_kanban")
    util.change_field_selection_values(
        cr,
        "account.report",
        "default_opening_date_filter",
        {
            "last_month": "previous_month",
            "last_quarter": "previous_quarter",
            "last_year": "previous_year",
            "last_tax_period": "previous_tax_period",
        },
    )
    if util.module_installed(cr, "sale"):
        util.move_field_to_module(cr, "account.move.line", "is_downpayment", "sale", "account")
    else:
        util.create_column(cr, "account_move_line", "is_downpayment", "bool", default=False)
