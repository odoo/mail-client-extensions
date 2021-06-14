from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["fix_fk_allowed_cascade"].append(("account_partial_reconcile", "debit_move_id"))
    util.ENVIRON["fix_fk_allowed_cascade"].append(("account_partial_reconcile", "credit_move_id"))
