# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "portal.portal_archive_groups")
    util.rename_xmlid(cr, "portal.portal_show_sign_in", "portal.user_sign_in")
