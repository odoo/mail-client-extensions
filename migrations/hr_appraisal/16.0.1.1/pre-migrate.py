from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr, "hr.appraisal.goal", "progression", {"0": "000", "25": "025", "50": "050", "75": "075"}
    )

    util.remove_field(cr, "hr.appraisal", "previous_appraisal_id")
    util.remove_field(cr, "hr.appraisal", "previous_appraisal_date")
