from odoo.upgrade import util


def migrate(cr, version):
    # Avoid sending 100k cv to ocr...
    util.create_column(cr, "hr_applicant", "is_first_stage", "boolean", default=False)
    util.create_column(cr, "hr_applicant", "state_processed", "boolean", default=False)
    util.create_column(cr, "hr_applicant", "extract_state", "varchar", default="no_extract_requested")
    util.create_column(cr, "hr_applicant", "extract_remote_id", "int4", default=-1)
