from odoo.tools import sql

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "forum.forum", "menu_id")
    sql.rename_column(cr, "forum_tag_rel", "forum_id", "forum_post_id")
