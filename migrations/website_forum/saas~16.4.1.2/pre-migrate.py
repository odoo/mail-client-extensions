from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "forum_waiting_posts_count")
    util.remove_field(cr, "forum.forum", "allow_bump")

    util.remove_view(cr, "website_forum.forum_nav_header")
    util.remove_view(cr, "website_forum.forum_post_options")
    util.remove_view(cr, "website_forum.moderation_display_post_answer")
    util.remove_view(cr, "website_forum.post_answers")
    util.remove_view(cr, "website_forum.question_dropdown")
    util.remove_view(cr, "website_forum.tag")

    util.explode_execute(cr, "UPDATE forum_post SET bump_date = write_date", table="forum_post")

    util.rename_field(cr, "forum.post", "bump_date", "last_activity_date")

    util.change_field_selection_values(
        cr,
        "forum.forum",
        "default_order",
        {"write_date desc": "last_activity_date desc"},
    )
