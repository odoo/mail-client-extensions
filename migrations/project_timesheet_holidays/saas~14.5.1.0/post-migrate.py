# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute(
        """ SELECT rcl.id
              FROM resource_calendar_leaves as rcl
              JOIN res_company as company ON rcl.company_id = company.id
             WHERE rcl.resource_id is null
               AND rcl.date_to >= now() at time zone 'UTC'
               AND company.internal_project_id is not null
        """
    )
    global_leaves_ids = cr.fetchall()
    global_leaves_ids = [key for (key,) in global_leaves_ids]
    for leave in util.iter_browse(env["resource.calendar.leaves"], global_leaves_ids):
        leave._timesheet_create_lines()
