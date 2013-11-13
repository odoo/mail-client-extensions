# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE message is in RST
    message = """
        * New tool to merge duplicated partners.
        * New Sales Team Dashboard, including spark lines.
        * Improved geolocalisation of Leads.
        * New mass-forward wizard for Leads.
        * Dynamic stages on leads, opportunities, tasks, issues and job applicants. You may need to adapt some of your custom search filters.
        * Folded stages are now available as a drop-down menu in the top right stage bar on Leads, Opportunities, Issues and Applicants.
        * Better leave pre-validation in HR module.
        * Social aspects for partners and employees.
        * Remove ``Shop`` model. The location is directly selectable on the Sale Order.
        * You can now choose the currency directly on the Purchase Order.
        * Improvement management of marketing campaigns with bounce processing.
        * Better Google Doc integration, including new ``google_spreadsheet`` module.
        * Easier Server and Automated Actions configuration.
    """
    util.announce(cr, message)
