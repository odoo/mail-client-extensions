from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "discuss.channel.member", "partner_email")
