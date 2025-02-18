from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    user = env["res.users"].browse(util.ref(cr, "base.default_user"))
    env["ir.config_parameter"].set_param("calendar.default_privacy", user.calendar_default_privacy)
