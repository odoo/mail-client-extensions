from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM helpdesk_team
         WHERE use_helpdesk_timesheet = true
         LIMIT 1
    """
    )
    if cr.rowcount:
        groups = util.env(cr).ref("helpdesk.group_helpdesk_user") + util.env(cr).ref(
            "hr_timesheet.group_hr_timesheet_user"
        )
        groups.write(
            {
                "implied_ids": [(4, util.ref(cr, "helpdesk_timesheet.group_use_helpdesk_timesheet"))],
            }
        )
