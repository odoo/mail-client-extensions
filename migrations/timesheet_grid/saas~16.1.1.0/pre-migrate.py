# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("timesheet_grid.timesheet_reminder{_manager,}"))
    cron_id = util.ref(cr, "timesheet_grid.timesheet_reminder")
    cr.execute(
        """
        UPDATE ir_act_server s
           SET code = 'model._cron_timesheet_reminder()'
          FROM ir_cron c
         WHERE c.ir_actions_server_id = s.id
           AND s.usage = 'ir_cron'
           AND c.id = %s
    """,
        [cron_id],
    )
    util.if_unchanged(cr, "timesheet_grid.mail_template_timesheet_reminder", util.update_record_from_xml)
    renames = {
        "res.company": {
            "timesheet_mail_manager_allow": "timesheet_mail_allow",
            "timesheet_mail_manager_delay": "timesheet_mail_delay",
            "timesheet_mail_manager_interval": "timesheet_mail_interval",
            "timesheet_mail_manager_nextdate": "timesheet_mail_nextdate",
        },
        "res.config.settings": {
            "reminder_manager_interval": "reminder_interval",
            "reminder_manager_delay": "reminder_delay",
        },
    }
    for model, ren in renames.items():
        for f, t in ren.items():
            util.rename_field(cr, model, f, t)
