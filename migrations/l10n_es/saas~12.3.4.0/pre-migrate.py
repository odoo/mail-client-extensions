# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_es.mod_115_02{03,}"))
    util.rename_xmlid(cr, *eb("l10n_es.mod_303_01{03,}"))
