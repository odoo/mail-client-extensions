from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "social.post.template", "has_twitter_accounts")
