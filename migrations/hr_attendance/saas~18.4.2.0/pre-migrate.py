from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_attendance", "in_location", "varchar")
    util.create_column(cr, "hr_attendance", "out_location", "varchar")
    util.explode_execute(
        cr,
        """
        UPDATE hr_attendance
           SET in_location = CONCAT_WS(', ', NULLIF(in_city, ''), NULLIF(in_country_name, '')),
               out_location = CONCAT_WS(', ', NULLIF(out_city, ''), NULLIF(out_country_name, ''))
        """,
        table="hr_attendance",
    )

    util.remove_field(cr, "hr.attendance", "in_city")
    util.remove_field(cr, "hr.attendance", "in_country_name")
    util.remove_field(cr, "hr.attendance", "out_city")
    util.remove_field(cr, "hr.attendance", "out_country_name")
