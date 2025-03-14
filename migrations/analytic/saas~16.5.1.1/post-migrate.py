from odoo.upgrade import util


def migrate(cr, version):
    util.env(cr)["account.analytic.plan"]._parent_store_compute()
