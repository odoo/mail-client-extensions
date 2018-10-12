# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    ICP = util.env(cr)["ir.config_parameter"]
    util.create_column(cr, "ir_attachment", "key", "varchar")
    util.create_column(cr, "ir_attachment", "website_id", "int4")
    util.create_column(cr, "res_config_settings", "module_website_links", "boolean")
    util.remove_field(cr, "res.config.settings", "google_maps_api_key")
    util.remove_field(cr, "res.config.settings", "has_google_analytics")
    util.remove_field(cr, "res.config.settings", "has_google_analytics_dashboard")
    util.remove_field(cr, "res.config.settings", "has_google_maps")

    util.create_column(cr, "res_partner", "website_id", "int4")
    util.create_column(cr, "res_users", "website_id", "int4")

    util.create_column(cr, "website", "social_twitter", "varchar")
    util.create_column(cr, "website", "social_facebook", "varchar")
    util.create_column(cr, "website", "social_github", "varchar")
    util.create_column(cr, "website", "social_linkedin", "varchar")
    util.create_column(cr, "website", "social_youtube", "varchar")
    util.create_column(cr, "website", "social_googleplus", "varchar")
    util.create_column(cr, "website", "social_instagram", "varchar")
    util.create_column(cr, "website", "google_maps_api_key", "varchar")
    util.create_column(cr, "website", "theme_id", "int4")
    util.create_column(cr, "website", "specific_user_account", "boolean")
    util.create_column(cr, "website", "auth_signup_uninvited", "varchar")

    for model in [
        "res.partner",
        "res.partner.grade",
        "res.partner.tag",
        "website.page",
        "blog.post",
        "event.event",
        "event.track",
        "hr.employee",
        "hr.job",
        "im_livechat.channel",
        "product.template",
        "delivery.carrier",
        "slide.channel",
        "slide.slide",
        "calendar.appointment.type",
        "helpdesk.team",
        "website.twitter.wall",
    ]:
        util.rename_field(cr, model, "website_published", "is_published")

    cr.execute(
        """
        UPDATE website
        SET social_twitter=c.social_twitter,
            social_facebook=c.social_facebook,
            social_github=c.social_github,
            social_linkedin=c.social_linkedin,
            social_youtube=c.social_youtube,
            social_googleplus=c.social_googleplus,
            social_instagram=c.social_instagram
        FROM res_company c
        WHERE website.company_id=c.id
    """
    )

    params = [("google_maps_api_key", "google_maps_api_key"), ("auth_signup_uninvited", "auth_signup.invitation_scope")]
    for field, key in params:
        param_value = ICP.get_param(key)
        if param_value:
            cr.execute("UPDATE website set {}=%s".format(field), (param_value,))

    util.create_column(cr, "website_page", "header_overlay", "boolean")
    util.create_column(cr, "website_page", "header_color", "varchar")
    util.create_column(cr, "website_page", "website_id", "int4")
    cr.execute(
        """
        UPDATE website_page p
        SET website_id=v.website_id
        FROM ir_ui_view v
        WHERE p.view_id=v.id
    """
    )

    util.remove_field(cr, "website.page", "website_ids")
    cr.execute("DROP TABLE IF EXISTS website_website_page_rel")
