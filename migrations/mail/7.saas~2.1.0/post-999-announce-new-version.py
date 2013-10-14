# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in RST
    message = """
        * New tool to merge duplicated partners.
        * New Sales Team Dashboard.
        * Improve geolocalisation of leads.
        * New lead mass forward wizard.
        * Dynamic stages on leads, opportunities, tasks, issues and job applicants.
        * Better leave pre-validation in HR module.
        * Social aspects for partners and employees.
        * Remove ``Shop`` model. The location is directly selectable on the Sale Order.
        * You can now choose the currency directly on the Purchase Order.
        * Better Google Doc integration, including new ``google_spreadsheet`` module.
        * Easier Server and Automated Actions configuration.
    """
    util.announce(cr, message)
