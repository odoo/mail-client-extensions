from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.line", "last_followup_date")
    util.remove_field(cr, "account.move.line", "next_action_date")

    util.remove_view(cr, "account_followup.customer_statements_form_view")
    util.remove_view(cr, "account_followup.account_followup_journal_dashboard_kanban_view")
    util.remove_record(cr, "account_followup.action_view_list_customer_statements")
    util.remove_menus(cr, [util.ref(cr, "account_followup.customer_statements_menu")])
