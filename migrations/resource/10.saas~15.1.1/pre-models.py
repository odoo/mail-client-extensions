# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'resource_calendar_leaves', 'tz', 'varchar')
    cr.execute("""
        UPDATE resource_calendar_leaves l
           SET tz = p.tz
          FROM res_users u
          JOIN res_partner p ON (p.id = u.partner_id)
         WHERE l.create_uid = u.id
    """)

    util.remove_field(cr, 'resource.calendar', 'manager')
    # should be removed by `hr_holidays` migration script, but as this field is required and
    # we are about to create some resource.calendar, we delete it now...
    util.remove_field(cr, 'resource.calendar', 'uom_id')

    util.create_column(cr, 'res_company', 'resource_calendar_id', 'int4')

    cr.execute("""
        WITH cal AS (
            INSERT INTO resource_calendar(name, company_id)
                 SELECT 'Standard 40 hours/week', id
                   FROM res_company
              RETURNING id, company_id
        )
        UPDATE res_company c
           SET resource_calendar_id = cal.id
          FROM cal
         WHERE cal.company_id = c.id
    """)
