from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "account.analytic.distribution")
    has_fk = bool(util.get_fk(cr, "account_analytic_tag"))
    util.remove_model(cr, "account.analytic.tag", drop_table=not has_fk)
