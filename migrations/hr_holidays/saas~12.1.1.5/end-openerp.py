# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _db_openerp(cr, version):
    env = util.env(cr)

    hr_holidays_manager = util.ref(cr, 'hr_holidays.group_hr_holidays_manager')
    hr_holidays_user = util.ref(cr, 'hr_holidays.group_hr_holidays_user')
    hr_teanlead = util.ref(cr, 'hr_holidays.group_hr_holidays_team_leader')
    excluded_uids = {
        hr_holidays_manager: (1239, 428676, 59, 248265, 15, 933484, 139),
        hr_holidays_user: (931332, 802165, 936102, 855448, 91, 941113, 813449, 1077640, 603085, 1285, 975712)
    }

    for group in (hr_holidays_manager, hr_holidays_user):
        for uid in env['res.users'].search(['&', ('groups_id', '=', group), '!', ('id', 'in', excluded_uids[group])]):
            uid.write({'groups_id': [(3, group), (4, hr_teanlead)]})


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
