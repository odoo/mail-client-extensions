from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "discuss.channel.member", "partner_email")

    util.remove_field(cr, "res.config.settings", "primary_color")
    util.remove_field(cr, "res.config.settings", "secondary_color")
