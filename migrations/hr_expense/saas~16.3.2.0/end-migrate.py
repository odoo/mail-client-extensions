from odoo.upgrade import util


def migrate(cr, version):
    # A new state is created, splitting the "reported" state into two new states
    cr.execute("SELECT id FROM hr_expense WHERE state IN ('draft', 'reported')")
    ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, "hr.expense", ["state"], ids=ids)
