from odoo.upgrade import util


def migrate(cr, version):
    if version.startswith(("saas~18.2.", "saas~18.3.")):
        module = "account_fiscal_categories" if util.version_gte("saas~18.5") else "account_disallowed_expenses"
        util.remove_record(cr, f"{module}.disallowed_expenses_report_disallowed_amount")
        cr.execute("""
            UPDATE account_disallowed_expenses_rate
            SET rate = ABS(rate - 100.0);
        """)
