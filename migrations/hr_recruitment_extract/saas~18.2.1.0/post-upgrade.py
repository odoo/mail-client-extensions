from odoo.upgrade import util


def migrate(cr, version):
    query = "SELECT id FROM hr_applicant WHERE candidate_id IS NULL"
    util.recompute_fields(cr, "hr.applicant", ["is_in_extractable_state"], query=query)
