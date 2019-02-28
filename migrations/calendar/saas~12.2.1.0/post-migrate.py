# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        DELETE FROM ir_config_parameter
              WHERE "key" = 'calendar.last_notif_mail'
          RETURNING value
    """
    )
    if cr.rowcount:
        lastcall = cr.fetchone()[0]
        cron = util.ref(cr, "calendar.ir_cron_scheduler_alarm")
        cr.execute("UPDATE ir_cron SET lastcall = %s WHERE id = %s", [lastcall, cron])
