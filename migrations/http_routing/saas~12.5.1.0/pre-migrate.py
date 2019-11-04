# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("{website,http_routing}.http_error"))
    util.rename_xmlid(cr, *eb("{website,http_routing}.http_error_debug"))
    util.rename_xmlid(cr, *eb("{website,http_routing}.403"))
    util.rename_xmlid(cr, *eb("{website,http_routing}.404"))
    util.rename_xmlid(cr, *eb("{website,http_routing}.500"))
