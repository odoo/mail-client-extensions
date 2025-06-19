from odoo.upgrade import util


def migrate(cr, version):
    if not version.startswith(("saas~18.2.", "saas~18.3.")):
        return
    util.remove_record(cr, "account_disallowed_expenses.disallowed_expenses_report_disallowed_amount")
    cr.execute("""
        UPDATE account_disallowed_expenses_rate
        SET rate = ABS(rate - 100.0);
    """)
