from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_consolidation.qunit_suite")
