from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "im_livechat.channel", "buffer_time")
    util.remove_field(cr, "discuss.channel", "anonymous_name")
