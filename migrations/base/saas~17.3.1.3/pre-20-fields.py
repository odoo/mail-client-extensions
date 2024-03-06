from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE ir_cron SET active = false WHERE numbercall = 0 AND active")
    util.remove_field(cr, "ir.cron", "doall")
    util.remove_field(cr, "ir.cron", "numbercall")
