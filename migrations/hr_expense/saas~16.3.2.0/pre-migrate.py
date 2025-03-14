from odoo.upgrade import util


def migrate(cr, version):
    # Remove unused field that has been added in 16.0 as part of a fix,
    # but became irrelevant in 16.2 as it is the same as 'journal_id'.
    util.remove_field(cr, "hr.expense.sheet", "journal_displayed_id")

    # Remove dead code, amount_residual is only relevant on the sheet and
    # not on the expense.
    util.remove_field(cr, "hr.expense", "amount_residual")
