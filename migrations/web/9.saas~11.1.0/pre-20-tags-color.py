# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # colors 10 and 0 for m2m tags in kanban views have been swapped.
    # See https://github.com/odoo/odoo/commit/fe66472e2cf7844c21ec438921307330ae562668
    tag_tables = util.splitlines("""
        account_account_tag
        account_analytic_tag
        crm_lead_tag
        fleet_vehicle_tag
        hr_employee_category
        hr_equipment_category
        hr_applicant_category
        mail_mass_mailing_tag
        note_tag
        project_tags
        event_track_tag
        res_partner_category
    """)
    for table in tag_tables:
        if util.column_exists(cr, table, 'color'):
            cr.execute("""
                UPDATE {0}
                   SET color=CASE WHEN color = 0 THEN 10
                                  WHEN color = 10 THEN 0
                                  ELSE color END
            """.format(table))
