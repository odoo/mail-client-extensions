from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "im_livechat.qunit_embed_suite")
