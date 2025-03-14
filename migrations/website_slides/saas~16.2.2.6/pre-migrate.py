from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_slides.rule_slide_channel_not_website")
    util.remove_record(cr, "website_slides.rule_slide_slide_not_website")
    query = """
        UPDATE slide_channel
           SET enroll = 'invite'
         WHERE visibility = 'members'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="slide_channel"))

    util.remove_field(cr, "slide.channel", "karma_gen_slide_vote")
