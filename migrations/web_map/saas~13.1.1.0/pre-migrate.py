# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("web_map.res_partner_{web_map_form,view_form_inherit_map}"), noupdate=False)
