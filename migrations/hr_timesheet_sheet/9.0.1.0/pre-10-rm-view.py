# -*- coding: utf-8 -*-

def migrate(cr, version):
    # This is not the view you are expecting for...
    cr.execute("DROP VIEW IF EXISTS hr_timesheet_sheet_sheet_account")
