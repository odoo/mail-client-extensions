from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "mail"):
        util.move_field_to_module(cr, "res.partner", "im_status", "bus", "mail")
        util.move_field_to_module(cr, "res.users", "im_status", "bus", "mail")
        util.rename_model(cr, "bus.presence", "mail.presence")
        for field_name in ["user_id", "last_poll", "last_presence", "status"]:
            util.move_field_to_module(cr, "mail.presence", field_name, "bus", "mail")
    else:
        util.remove_field(cr, "res.partner", "im_status")
        util.remove_field(cr, "res.users", "im_status")
        util.remove_model(cr, "bus.presence")
