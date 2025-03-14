from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "social.account", "twitter_screen_name", "social_twitter", "social")
    util.rename_field(cr, "social.account", "twitter_screen_name", "social_account_handle")
