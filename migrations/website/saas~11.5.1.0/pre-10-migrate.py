from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    ICP = util.env(cr)["ir.config_parameter"]
    util.create_column(cr, "ir_attachment", "key", "varchar")
    util.create_column(cr, "ir_attachment", "website_id", "int4")
    util.create_column(cr, "res_config_settings", "module_website_links", "boolean")
    util.remove_column(cr, "res_config_settings", "google_maps_api_key")
    util.remove_column(cr, "res_config_settings", "has_google_analytics")
    util.remove_column(cr, "res_config_settings", "has_google_analytics_dashboard")
    util.remove_column(cr, "res_config_settings", "has_google_maps")

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

    # Populate website theme_id with the installed theme so that it get loaded in 12.0
    #
    # Get the ids (and names) of the installed_themes (except hidden ones) ... they are in state='to upgrade' during migration
    # LEFT JOIN with ir_module_module_dependency ON the name to get the (child) themes (in module_id) depending on these installed themes
    # LEFT JOIN with the installed_themes on id=module_id to "mark" the installed themes with an installed 'child'
    # GROUP by id and keep the one that is not "marked" [HAVING array_to_string(array_agg(dt.id), '') = '']

    query = """
            WITH installed_themes AS (
            SELECT id,name
              FROM ir_module_module
             WHERE state = 'to upgrade'
               AND (name = 'theme_default'
                OR category_id IN (
                    SELECT id
                      FROM ir_module_category
                     WHERE parent_id = (
                            SELECT res_id
                              FROM ir_model_data
                             WHERE module = 'base'
                               AND name = 'module_category_theme'
                           )
                       AND id != (
                            SELECT res_id
                              FROM ir_model_data
                             WHERE module = 'base'
                               AND name = 'module_category_theme_hidden'
                           )
                     UNION
                    SELECT res_id
                      FROM ir_model_data
                     WHERE module = 'base'
                       AND name = 'module_category_theme'
                   ))
            ),
            leaf_themes AS (
                SELECT t.id
                  FROM installed_themes t
             LEFT JOIN ir_module_module_dependency d ON t.name = d.name
             LEFT JOIN installed_themes dt ON dt.id = d.module_id
              GROUP BY t.id
                HAVING array_to_string(array_agg(dt.id), '') = ''
            )
            UPDATE website w
                  SET theme_id = i.id
              FROM leaf_themes i
            WHERE w.id = 1
         """
    cr.execute(query)

    params = [("google_maps_api_key", "google_maps_api_key"), ("auth_signup_uninvited", "auth_signup.invitation_scope")]
    for field, key in params:
        param_value = ICP.get_param(key)
        if param_value:
            cr.execute(util.format_query(cr, "UPDATE website set {}=%s", field), (param_value,))

    cr.execute(
        """
        DELETE FROM ir_config_parameter
              WHERE key IN ('google_maps_api_key',
                            'website.has_google_analytics',
                            'website.has_google_analytics_dashboard',
                            'website.has_google_maps'
                           )
    """
    )

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
