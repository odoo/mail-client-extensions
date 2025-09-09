from odoo.upgrade import util


def migrate(cr, version):
    # A new state is created, splitting the "reported" state into two new states
    query = "SELECT id FROM hr_expense WHERE state IN ('draft', 'reported')"
    util.recompute_fields(cr, "hr.expense", ["state"], query=query)
