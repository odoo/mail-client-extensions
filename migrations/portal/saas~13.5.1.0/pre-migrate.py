# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "ir.ui.view", "customize_show", "website", "portal")
    util.create_column(cr, "ir_ui_view", "customize_show", "boolean", default=False)

    util.remove_view(cr, "portal.portal_archive_groups")
    util.rename_xmlid(cr, "portal.portal_show_sign_in", "portal.user_sign_in")
