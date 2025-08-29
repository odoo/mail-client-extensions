from odoo.upgrade import util


def migrate(cr, version):
    if not util.version_gte("saas~18.4"):
        # Disallowed rate field becomes Deductible rate
        cr.execute("UPDATE fleet_disallowed_expenses_rate SET rate = 100.0 - rate")
