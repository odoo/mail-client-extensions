# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, *util.expand_braces('web{site,}.pdf_js_lib'))
    views = util.splitlines("""
        layout
        qunit_suite
        webclient_bootstrap
        pdf_js_lib
    """)
    for v in views:
        util.force_noupdate(cr, 'web.' + v, False)
