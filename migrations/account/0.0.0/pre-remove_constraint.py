from odoo.addons.base.maintenance.migrations.util import version_gte


def migrate(cr, version):
    if version_gte("14.0"):
        cr.execute("ALTER TABLE account_move_line DROP CONSTRAINT IF EXISTS account_move_line_credit_debit1")
        cr.execute("ALTER TABLE account_move_line DROP CONSTRAINT IF EXISTS account_move_line_credit_debit2")
