from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "website_slides.rule_slide_slide_signed_in_user")
    util.update_record_from_xml(cr, "website_slides.rule_slide_channel_visibility_signed_in_user")

    util.if_unchanged(cr, "website_slides.rule_slide_slide_resource_downloadable", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.mail_template_slide_channel_enroll", util.update_record_from_xml)
    util.if_unchanged(cr, "website_slides.mail_notification_channel_invite", util.update_record_from_xml)
    extra_filter = cr.mogrify("t.id = %s", [util.ref(cr, "website_slides.view_slide_channel_form")]).decode()
    util.replace_in_all_jsonb_values(
        cr,
        "ir_ui_view",
        "arch_db",
        "members_done_count_label",
        "members_completed_count_label",
        extra_filter=extra_filter,
    )
