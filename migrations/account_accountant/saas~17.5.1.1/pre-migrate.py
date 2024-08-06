from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "period_lock_date")
    util.remove_field(cr, "res.config.settings", "fiscalyear_lock_date")
    util.remove_field(cr, "res.config.settings", "tax_lock_date")

    util.remove_field(cr, "account.change.lock.date", "period_lock_date")
    util.rename_field(cr, "bank.rec.widget", "st_line_to_check", "st_line_checked")
