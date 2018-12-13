# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # data being in noupdate, manually update types

    env = util.env(cr)
    ref = lambda r: util.ref(cr, "hr_holidays." + r)
    env.ref("hr_holidays.holiday_status_cl").write(
        {"leave_notif_subtype_id": ref("mt_leave"), "allocation_notif_subtype_id": ref("mt_leave_allocation")}
    )
    env.ref("hr_holidays.holiday_status_sl").write({"leave_notif_subtype_id": ref("mt_leave_sick")})
    env.ref("hr_holidays.holiday_status_comp").write({"leave_notif_subtype_id": ref("mt_leave")})
    env.ref("hr_holidays.holiday_status_unpaid").write({"leave_notif_subtype_id": ref("mt_leave_unpaid")})
