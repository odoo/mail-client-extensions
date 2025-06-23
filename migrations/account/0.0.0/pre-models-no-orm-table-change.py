from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["_no_orm_table_change"] |= {
        "account.move",
        "account.move.line",
        "account.bank.statement",
        "account.bank.statement.line",
    }
