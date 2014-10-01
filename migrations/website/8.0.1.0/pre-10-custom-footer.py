# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from lxml import etree

def migrate(cr, version):

    # Force reset of main layout ... it was changed too much due to
    # the new bundles, as of rev. 74d4d1f.
    util.force_noupdate(cr, 'website.layout', False)

    # Fix custom footer by adding an @id='footer' to make it compatible w/ new one
    footer_custom_view_id = util.ref(cr, 'website.footer_custom')
    if not footer_custom_view_id:
        return
    cr.execute(
        "select arch from ir_ui_view where id = %s",
        [footer_custom_view_id]
    )
    arch_data, = cr.fetchone()
    arch = etree.fromstring(arch_data)
    divs = arch.xpath('//div')
    if divs:
        div = divs[0]
        div.attrib['id'] = 'footer'
        new_arch = etree.tostring(arch)
        cr.execute(
            "update ir_ui_view set arch = %s where id = %s",
            [new_arch, footer_custom_view_id])
