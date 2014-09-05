# -*- coding: utf-8 -*-
import lxml

from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    website_layout = util.ref(cr, 'website.layout')
    if not website_layout:
        return
    cr.execute("SELECT arch FROM ir_ui_view WHERE id = %s",
               [website_layout])
    arch = lxml.etree.fromstring(cr.fetchone()[0])

    # New in version 8:
    #   - call assets web.assets_common
    #   - call assets website.assets_frontend
    if not arch.find('.//t[@t-call-assets="website.assets_frontend"]'):
        layout_head = arch.find('.//t[@name="layout_head"]')
        assert layout_head is not None
        for asset in ["web.assets_common", "website.assets_frontend"]:
            layout_head.addprevious(
                lxml.etree.Element('t', {'t-call-assets': asset}))

    cr.execute("UPDATE ir_ui_view SET arch = %s WHERE id = %s",
               [lxml.etree.tostring(arch), website_layout])
