# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("web.external_layout_{clean,bold}"))
    util.rename_xmlid(cr, *eb("web.external_layout_{background,striped}"))
    util.rename_xmlid(cr, *eb("web.report_layout_{clean,bold}"))
    util.rename_xmlid(cr, *eb("web.report_layout_{background,striped}"))
