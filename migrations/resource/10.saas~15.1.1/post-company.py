# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    Calendar = util.env(cr)['resource.calendar']
    cr.execute("SELECT resource_calendar_id FROM res_company")
    for cid, in cr.fetchall():
        cal = Calendar.browse(cid)
        cal.attendance_ids = cal._get_default_attendance_ids()
