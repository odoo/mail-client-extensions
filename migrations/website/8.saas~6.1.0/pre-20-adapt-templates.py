# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xids = util.splitlines("""
        assets_frontend
        layout      # main layout should not be modified
        layout_footer_copyright
        editor_head
        assets_common
        assets_editor
        snippets
        publish_short
        theme_customize
    """)
    for x in xids:
        util.force_noupdate(cr, 'website.' + x, False)

    util.rename_xmlid(cr, 'website.editor_head', 'website.layout_editor')

    util.remove_view(cr, 'website.theme')
    util.remove_view(cr, 'website.themes')

    # footers now attach to #footer
    with util.skippable_cm(), util.edit_view(cr, 'website.footer_custom') as arch:
        for node in arch.xpath("//xpath[contains(@expr, 'footer_container')]"):  # xpathception!
            node.attrib['expr'] = node.attrib['expr'].replace('footer_container', 'footer')

        node = arch.find('.//section[@data-snipet-id]')
        if node:
            del node.attrib['data-snippet-id']

    with util.skippable_cm(), util.edit_view(cr, 'website.footer_default') as arch:
        node = arch.find('.//div')
        node.attrib['id'] = "footer"

    with util.skippable_cm(), util.edit_view(cr, 'website.aboutus') as arch:
        for node in arch.xpath('//section[@data-snipet-id]'):
            del node.attrib['data-snippet-id']
