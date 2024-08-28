from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "social.stream.post", "youtube_likes_ratio")
