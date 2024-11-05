from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_forum.forum_post_view_kanban", util.update_record_from_xml)
