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
    """)
    for x in xids:
        util.force_noupdate(cr, 'website.' + x, False)

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

    # ensure themes (beside they moved to another module) are loaded last
    cr.execute("""UPDATE ir_ui_view v
                     SET priority=24
                    FROM ir_model_data d
                   WHERE d.model='ir.ui.view'
                     AND v.id=d.res_id
                     AND d.module='website'
                     AND d.name IN ('theme_amelia', 'theme_cerulean', 'theme_cosmo',
                                    'theme_cyborg', 'theme_flatly', 'theme_journal',
                                    'theme_readable', 'theme_simplex', 'theme_slate',
                                    'theme_spacelab', 'theme_united', 'theme_yeti')
               """)
