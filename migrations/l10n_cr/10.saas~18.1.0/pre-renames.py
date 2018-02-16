# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    titles = 'pvt_ltd ltd sal asoc gov edu indprof dra msc mba lic licda ing'.split()
    for title in titles:
        util.rename_xmlid(cr, *eb('{base,l10n_cr}.res_partner_title_' + title))
