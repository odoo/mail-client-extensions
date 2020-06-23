# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DROP TABLE IF EXISTS website_visitor_partner_rel")

    util.create_column(cr, "website", "custom_code_head", "text")
    util.create_column(cr, "website", "custom_code_footer", "text")

    util.create_column(cr, "website", "has_social_default_image", "boolean")
    cr.execute(
        """
        UPDATE
            website w
        SET
            has_social_default_image=EXISTS(
                SELECT 1
                FROM ir_attachment a
                WHERE a.res_id = w.id
                  AND a.res_model = 'website'
                  AND a.res_field = 'social_default_image'
            )
    """
    )

    util.remove_record(cr, "website.access_website")
    util.remove_record(cr, "website.access_seo_manager")

    util.rename_xmlid(cr, "website.options_s_timeline", "website.s_timeline_options")
