# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('website.access_website{,_designer}'))
    util.rename_xmlid(cr, *eb('website.access_seo_{public,manager}'))
