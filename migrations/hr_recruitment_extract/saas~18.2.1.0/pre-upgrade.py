from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_applicant", "extract_state", "varchar", default="no_extract_requested")
    util.create_column(cr, "hr_applicant", "is_in_extractable_state", "boolean")
    util.create_column(cr, "hr_applicant", "extract_state_processed", "boolean")

    query = """
        UPDATE hr_applicant a
           SET extract_state = c.extract_state,
               is_in_extractable_state = c.is_in_extractable_state,
               extract_state_processed = c.extract_state_processed
          FROM hr_candidate c
         WHERE c.id = a.candidate_id
    """
    util.explode_execute(cr, query, table="hr_applicant", alias="a")
