# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT bool_or(website_form_enable_metadata) FROM website")
    if cr.fetchone()[0]:
        util.env(cr)["ir.config_parameter"].set_param("website_form_enable_metadata", True)

    util.remove_field(cr, "website", "website_form_enable_metadata")
    util.remove_field(cr, "res.config.settings", "website_form_enable_metadata")

    gone = """
        res_config_settings_view_form

        assets_frontend
        register_s_website_form
        snippet_options
    """
    for view in util.splitlines(gone):
        util.remove_view(cr, f"website_form.{view}")
