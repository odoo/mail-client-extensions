# -*- coding: utf-8 -*-

# NOTE: This is a end- script to allow saas~17 to convert default values to ipc

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    prefixes = util.splitlines("""
        account
        attendance
        base
        event
        fleet
        hr
        hr.expense
        hr.payroll
        hr.recruitment
        hr.timesheet
        mass.mailing
        mrp
        project
        pos
        purchase
        sale
        stock
        website
    """)
    for prefix in prefixes:
        util.remove_model(cr, prefix + '.config.settings')
