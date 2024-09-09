from odoo.upgrade import util


def migrate(cr, version):
    util.env(cr)["res.groups"]._activate_group_account_secured()
