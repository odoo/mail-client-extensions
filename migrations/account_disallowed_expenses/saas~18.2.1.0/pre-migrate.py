from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~18.4"):
        # Disallowed rate field becomes Deductible rate
        cr.execute("UPDATE account_disallowed_expenses_rate SET rate = 100.0 - rate")
        util.add_to_migration_reports(
            message=""
            "Disallowed Expenses: Disallowed rates are replaced by Deductibility rates,"
            "allowing for deductiblity over 100%.",
            category="Accounting",
            format="md",
        )
