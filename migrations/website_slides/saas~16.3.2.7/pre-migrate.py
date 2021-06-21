# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "website_slides.mail_template_slide_channel_invite", "website_slides.mail_template_slide_channel_enroll"
    )

    util.create_column(cr, "slide_channel_invite", "enroll_mode", "boolean", default=True)
    util.create_column(cr, "slide_channel_invite", "send_email", "boolean", default=True)

    # Replace completed field with member_status
    util.create_column(cr, "slide_channel_partner", "member_status", "varchar")
    query = """
        UPDATE slide_channel_partner
           SET member_status =
             (CASE
                  WHEN completion = 0 THEN 'joined'
                  WHEN completion = 100 OR completed = True THEN 'completed'
                  ELSE 'ongoing'
               END)
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="slide_channel_partner"))

    util.rename_field(cr, "slide.channel", "members_done_count", "members_completed_count")
    util.update_record_from_xml(cr, "website_slides.rule_slide_slide_signed_in_user")
    util.update_record_from_xml(cr, "website_slides.rule_slide_channel_visibility_signed_in_user")

    def adapter(leaf, _, __):
        left, operator, right = leaf
        operator = "=" if bool(right) else "!="
        return [(left, operator, "completed")]

    util.update_field_usage(cr, "slide.channel.partner", "completed", "member_status", domain_adapter=adapter)
    util.remove_field(cr, "slide.channel.partner", "completed")
