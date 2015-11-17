#-*- encoding: utf8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for group in """configuration erp_manager hr_attendance hr_manager hr_user
        light_multi_company multi_company multi_currency no_one partner_manager
        portal public sale_manager sale_salesman sale_salesman_all_leads
        survey_manager survey_user system user website_designer
        website_publisher""".split():
        util.force_noupdate(cr, 'base.group_'+group, noupdate=False)

