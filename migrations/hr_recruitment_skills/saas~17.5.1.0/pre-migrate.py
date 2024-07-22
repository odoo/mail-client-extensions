from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "hr.applicant.skill", "hr.candidate.skill")
    util.create_column(cr, "hr_candidate_skill", "candidate_id", "int4", fk_table="hr_candidate")

    query = """
        UPDATE hr_candidate_skill cs
           SET candidate_id = a.candidate_id
          FROM hr_applicant a
         WHERE cs.applicant_id = a.id
    """
    util.explode_execute(cr, query, table="hr_candidate_skill", alias="cs")
    util.remove_field(cr, "hr.candidate.skill", "applicant_id")

    util.create_m2m(cr, "hr_candidate_hr_skill_rel", "hr_candidate", "hr_skill", "hr_candidate_id", "hr_skill_id")
    cr.execute(
        """
        INSERT INTO hr_candidate_hr_skill_rel (hr_candidate_id, hr_skill_id)
    SELECT DISTINCT candidate_id, skill_id
               FROM hr_candidate_skill;
        """
    )
    util.remove_field(cr, "hr.applicant", "applicant_skill_ids")

    util.remove_field(cr, "hr.applicant", "is_interviewer")
    util.remove_field(cr, "hr.applicant", "matching_skill_ids")
    util.remove_field(cr, "hr.applicant", "missing_skill_ids")
    util.remove_field(cr, "hr.applicant", "matching_score")

    util.remove_view(cr, "hr_recruitment_skills.crm_case_tree_view_inherit_hr_recruitment_skills")
