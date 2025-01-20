from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "discuss.channel", "allow_public_upload")
    util.remove_field(cr, "discuss.channel.member", "fold_state")
