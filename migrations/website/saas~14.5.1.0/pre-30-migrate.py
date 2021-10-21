# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "website_configurator_feature"):
        util.create_column(cr, "website_configurator_feature", "feature_url", "varchar")
        util.create_column(cr, "website_configurator_feature", "menu_company", "boolean")
        util.create_column(cr, "website_configurator_feature", "menu_sequence", "int4")
        util.remove_field(cr, "website.configurator.feature", "type")
        util.rename_field(
            cr, "website.configurator.feature", "website_types_preselection", "website_config_preselection"
        )

    # website_animate was merged into website but none of its views remains
    util.remove_view(cr, "website.o_animate_options")
    util.remove_view(cr, "website.no-js_fallback")

    # header template migration
    util.remove_view(cr, "website.template_header_default_oe_structure_header_default_1")
    util.remove_view(cr, "website.template_header_hamburger_oe_structure_header_hamburger_1")
    util.remove_view(cr, "website.template_header_slogan_oe_structure_header_slogan_2")
    util.remove_view(cr, "website.template_header_boxed_oe_structure_header_boxed_2")
    util.remove_view(cr, "website.template_header_image_oe_structure_header_image_2")

    # minimalist header to remove -> re-enable the default one on the right
    # websites (which should already have a cow'ed view for it but disabled)
    cr.execute("SELECT website_id FROM ir_ui_view WHERE key = 'website.template_header_minimalist' and active = TRUE")
    website_ids = [website_id for (website_id,) in cr.fetchall()]
    if website_ids:
        cr.execute(
            "UPDATE ir_ui_view SET active = TRUE WHERE key = 'website.template_header_default' and website_id IN %s",
            [tuple(website_ids)],
        )
    util.remove_view(cr, "website.template_header_minimalist")
