from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "social.post.template", "display_push_notification_attributes")
    for table in ("social_post", "social_post_template"):
        util.create_column(cr, table, "push_notification_message", "text")
        query = util.format_query(cr, "UPDATE {} SET push_notification_message = message", table)
        cr.execute(query)
