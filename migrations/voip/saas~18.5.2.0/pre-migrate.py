from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "should_auto_reject_incoming_calls")
    util.remove_field(cr, "res.users.settings", "should_auto_reject_incoming_calls")
