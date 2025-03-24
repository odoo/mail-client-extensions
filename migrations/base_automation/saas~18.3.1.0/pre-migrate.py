from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "base.automation", "least_delay_msg")

    # Convert trg_date_range with new trg_date_range_mode column
    util.create_column(cr, "base_automation", "trg_date_range_mode", "varchar")
    cr.execute("""
        UPDATE base_automation
           SET trg_date_range = ABS(trg_date_range),
               trg_date_range_mode = CASE WHEN trigger = 'on_time' AND trg_date_range < 0 THEN 'before'
                                          ELSE 'after'
                                      END
         WHERE trigger IN ('on_time', 'on_time_created', 'on_time_updated')
    """)
