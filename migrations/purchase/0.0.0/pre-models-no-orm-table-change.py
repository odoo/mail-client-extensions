from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["_no_orm_table_change"] |= {
        "purchase.order",
        "purchase.order.line",
    }
