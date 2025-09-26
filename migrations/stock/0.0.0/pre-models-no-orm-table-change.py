from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["_no_orm_table_change"] |= {
        "stock.move",
        "stock.move.line",
        "stock.quant",
    }
