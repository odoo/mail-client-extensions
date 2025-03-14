from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sign.send.request", "refusal_allowed")
    util.remove_field(cr, "sign.request", "refusal_allowed")
    util.remove_field(cr, "res.config.settings", "group_show_sign_order")
    util.remove_record(cr, "sign.show_sign_order")
