from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.bom", "schedule_count")

    util.create_column(cr, "res_company", "manufacturing_period_to_display_month", "int4", default=12)
    util.create_column(cr, "res_company", "manufacturing_period_to_display_week", "int4", default=12)
    util.create_column(cr, "res_company", "manufacturing_period_to_display_day", "int4", default=30)
    cr.execute("""
        UPDATE res_company
           SET manufacturing_period_to_display_month = manufacturing_period_to_display
         WHERE manufacturing_period = 'month'
    """)
    cr.execute("""
        UPDATE res_company
           SET manufacturing_period_to_display_week = manufacturing_period_to_display
         WHERE manufacturing_period = 'week'
    """)
    cr.execute("""
        UPDATE res_company
           SET manufacturing_period_to_display_day = manufacturing_period_to_display
         WHERE manufacturing_period = 'day'
    """)
    util.remove_field(cr, "res.company", "manufacturing_period_to_display")
    util.remove_field(cr, "res.config.settings", "manufacturing_period_to_display")
