# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        WITH c_res_cal AS (
            SELECT l.id AS leave_id,
                   MIN(c.resource_calendar_id) AS res_cal_id -- Should be the same resource calendar for all the contracts
              FROM hr_leave l
              JOIN hr_contract c
                ON c.employee_id = l.employee_id
               AND c.date_start <= l.date_to
               AND (c.date_end IS NULL OR c.date_end >= l.date_from)
               AND (c.state = 'open' OR c.state = 'close' OR (c.state = 'draft' AND c.kanban_state = 'done'))
               AND l.holiday_type = 'employee'
               AND {parallel_filter}
          GROUP BY l.id
        )

        UPDATE hr_leave l
           SET resource_calendar_id = c_res_cal.res_cal_id
          FROM c_res_cal
         WHERE l.id = c_res_cal.leave_id
        """,
        table="hr_leave",
        alias="l",
    )
