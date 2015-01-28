# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'crm.case.section', 'crm.team')
    cr.execute("ALTER TABLE sale_member_rel RENAME COLUMN section_id TO team_id")

    cr.execute("""UPDATE ir_model_data
                     SET name=replace(name, 'case_section', 'team')
                   WHERE module='sales_team'
               """)

    util.rename_xmlid(cr, 'sales_team.section_sales_department',
                          'sales_team.team_sales_department')

    util.remove_view(cr, 'sales_team.res_user_form')
    util.remove_view(cr, 'sales_team.view_users_form_preferences')
