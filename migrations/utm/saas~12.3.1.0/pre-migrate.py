# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("utm.utm_campaign_{tree,view_tree}"))
    util.rename_xmlid(cr, *eb("utm.utm_campaign_{form,view_form}"))

