# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'website.config.settings', 'module_website_version')
    util.remove_field(cr, 'website.config.settings', 'module_website_form_editor')
    util.rename_xmlid(cr, 'website.info', 'website.website_info')

    util.force_noupdate(cr, 'website.view_website_config_settings', False)
    util.force_noupdate(cr, 'website.layout', False)
