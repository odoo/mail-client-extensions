# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    vid = util.ref(cr, "website.affix_top_menu")
    if not vid:
        return

    cr.execute("SELECT active FROM ir_ui_view WHERE id = %s", [vid])
    if cr.fetchone()[0]:
        query = "UPDATE ir_ui_view SET active = %s WHERE id = %s"
        cr.execute(query, [False, util.ref(cr, "website.header_visibility_standard")])
        cr.execute(query, [True, util.ref(cr, "website.header_visibility_fixed")])

    util.remove_view(cr, "website.affix_top_menu")
