# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website.snippet_options_header_brand")

    # Google Analytics Dashboard deprecated
    util.remove_field(cr, "website", "google_management_client_id")
    util.remove_field(cr, "website", "google_management_client_secret")
    util.remove_field(cr, "res.config.settings", "google_management_client_id")
    util.remove_field(cr, "res.config.settings", "google_management_client_secret")
    util.remove_field(cr, "res.config.settings", "has_google_analytics_dashboard")
    util.rename_xmlid(
        cr, "website.ir_actions_server_website_google_analytics", "website.ir_actions_server_website_analytics"
    )
    util.rename_xmlid(cr, "website.menu_website_google_analytics", "website.menu_website_analytics")

    # Rename publisher into restricted editor
    util.rename_xmlid(cr, "website.group_website_publisher", "website.group_website_restricted_editor")
    cr.execute(
        r"""
        UPDATE ir_ui_view
           SET arch_db = jsonb_build_object(
                   'en_US',
                   REGEXP_REPLACE(
                       arch_db->>'en_US',
                       '\ywebsite\.group_website_publisher\y',
                       'website.group_website_restricted_editor',
                       'g'
                    ))
         WHERE arch_db->>'en_US' LIKE '%website.group\_website\_publisher%'
    """
    )
    util.rename_xmlid(
        cr, "website.access_website_ir_ui_view_publisher", "website.access_website_ir_ui_view_restricted_editor"
    )

    # Homepage refactoring
    util.create_column(cr, "website", "homepage_url", "varchar")
    cr.execute(
        """
        UPDATE website w
           SET homepage_url = p.url
          FROM website_page p
         WHERE w.homepage_id = p.id
           AND p.url != '/'
    """
    )
    util.remove_field(cr, "website", "homepage_id")
    util.remove_field(cr, "res.config.settings", "homepage_id")

    # Remove "multi website by country" and make domain unique
    cr.execute(
        """
        UPDATE website
           SET domain = NULL
         WHERE id IN (
             SELECT unnest((array_agg(id ORDER BY id))[2:])
               FROM website
           GROUP BY domain
             HAVING count(*) > 1
         )
    """
    )
    util.remove_field(cr, "website", "country_group_ids")
    cr.execute("DROP TABLE IF EXISTS website_country_group_rel")
    util.remove_field(cr, "res.config.settings", "website_country_group_ids")
