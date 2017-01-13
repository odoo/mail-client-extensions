# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        module_website_form_editor
        module_website_version
        compress_html
    """)
    for f in fields:
        util.remove_field(cr, 'website.config.settings', f)

    util.remove_field(cr, 'website', 'compress_html')

    util.remove_view(cr, 'website.view_website_config_settings')
