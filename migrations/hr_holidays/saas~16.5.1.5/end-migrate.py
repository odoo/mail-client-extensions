from odoo.upgrade import util


def migrate(cr, version):
    # Computing `number_of_hours` also updates `number_of_days`, which can have been changed by the user.
    # To keep any possible change we recover number_of_days from the original value.
    util.create_column(cr, "hr_leave", "_upg_number_of_days", "float")
    util.explode_execute(cr, "UPDATE hr_leave SET _upg_number_of_days = number_of_days", table="hr_leave")
    util.recompute_fields(cr, "hr.leave", ["number_of_hours"])
    util.explode_execute(
        cr,
        """
        UPDATE hr_leave
           SET number_of_days = _upg_number_of_days
         WHERE _upg_number_of_days IS DISTINCT FROM number_of_days
        """,
        table="hr_leave",
    )
    util.remove_column(cr, "hr_leave", "_upg_number_of_days")
