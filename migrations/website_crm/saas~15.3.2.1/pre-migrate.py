# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    script = util.import_script("website_crm/saas~15.2.2.1/pre-migrate.py")
    script.reenable_contactus_form_values(cr)

    util.remove_field(cr, "res.config.settings", "crm_default_team_id")
    util.remove_field(cr, "res.config.settings", "crm_default_user_id")
    util.remove_view(cr, "website_crm.res_config_settings_view_form")
