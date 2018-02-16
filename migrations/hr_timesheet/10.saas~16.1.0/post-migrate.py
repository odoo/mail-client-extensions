# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    gusr = util.ref(cr, 'hr_timesheet.group_hr_timesheet_user')
    gmng = util.ref(cr, 'hr_timesheet.group_timesheet_manager')
    ghru = util.ref(cr, 'hr.group_hr_user')
    gemp = util.ref(cr, 'base.group_user')

    # correct implied_id on gmng (use orm to handle users)
    util.env(cr)['res.groups'].browse(gmng).write({
        'implied_ids': [(6, 0, [gusr, ghru])],
    })

    # employees are users
    cr.execute("""
        INSERT INTO res_groups_users_rel(uid, gid)
             SELECT uid, %(gusr)s
               FROM res_groups_users_rel
              WHERE gid = %(gemp)s
             EXCEPT
             SELECT uid, gid
               FROM res_groups_users_rel
              WHERE gid = %(gusr)s
    """, locals())
