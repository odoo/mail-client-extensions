# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "calendar.contacts", "calendar.filters")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("calendar.access_calendar_{contacts,filters}_all"))
    util.rename_xmlid(cr, *eb("calendar.access_calendar_{contacts,filters}"))
