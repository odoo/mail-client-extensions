# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('{mrp_workorder,quality}.test_type_text'))
    util.rename_xmlid(cr, *eb('{mrp_workorder,quality}.test_type_picture'))
