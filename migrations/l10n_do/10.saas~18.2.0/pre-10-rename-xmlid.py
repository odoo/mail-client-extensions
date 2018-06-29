# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    titles = 'dra msc mba lic licda ing'.split()
    for title in titles:
        util.rename_xmlid(cr, *eb('{base,l10n_do}.res_partner_title_' + title))
