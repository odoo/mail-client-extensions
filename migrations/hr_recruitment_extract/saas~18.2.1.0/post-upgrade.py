from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM hr_applicant WHERE candidate_id IS NULL")
    if cr.rowcount:
        util.recompute_fields(cr, "hr.applicant", ["is_in_extractable_state"], ids=[rid for (rid,) in cr.fetchall()])
