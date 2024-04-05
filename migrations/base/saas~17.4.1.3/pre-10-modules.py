from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "data_merge", "data_cleaning")
    util.merge_module(cr, "im_livechat_mail_bot", "mail_bot")
