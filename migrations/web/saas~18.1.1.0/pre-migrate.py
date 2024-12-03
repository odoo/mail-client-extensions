from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web.qunit_mobile_suite")
