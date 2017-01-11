# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        module_share
        module_portal
        custom_footer
        rml_footer_readonly
        rml_paper_format
        font
        rml_header
        rml_header2
        rml_header3
    """)
    for field in fields:
        util.remove_field(cr, 'base.config.settings', field)

    # as config views have been rewritten, it's easier to simply delete base view
    util.remove_view(cr, 'base_setup.view_general_configuration')
