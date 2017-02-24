# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    views = util.splitlines("""
        theme_common.s_showcase_image_caption-opt
        theme_common.s_options_discount

        theme_clean.options_colorpicker
        theme_enark.options_colorpicker
        theme_nano.editor_colorpicker
        theme_treehouse.editor_colorpicker
    """)
    for v in views:
        util.remove_view(cr, v)

    for t in 'anelusia clean kea kiddo loftspace monglia notes'.split():
        util.remove_view(cr, 'theme_%s.colorpicker' % t)
