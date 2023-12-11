from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "working_days_count")
    util.remove_field(cr, "planning.analysis.report", "working_days_count")
    util.create_column(cr, "planning_slot_template", "end_time", "float")
    util.create_column(cr, "planning_slot_template", "duration_days", "integer")

    cr.execute(
        """
           UPDATE planning_slot_template
              SET duration_days =
                    CEIL((start_time + duration) / 24) +
                    -- This extra case is to manage the case we have start_time set to 8 o'clock
                    -- and a duration set to 16 hours and so the end_time will be 12am and so 2 duration_days.
                    CASE
                        WHEN start_time > 0 AND (start_time + duration)::numeric % 24 = 0
                        THEN 1
                        ELSE 0
                     END,
                  end_time = (start_time + duration)::numeric % 24
        """
    )

    util.remove_field(cr, "planning.slot.template", "duration")
