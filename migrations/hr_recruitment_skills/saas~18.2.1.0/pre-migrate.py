from odoo.upgrade import util


def migrate(cr, version):
    # Rename demo data to avoid issures
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_recruitment_skills.hr_{candidate,case}_mkt0_skill_lang_en"))
    util.rename_xmlid(cr, *eb("hr_recruitment_skills.hr_{candidate,case}_mkt0_skill_lang_fr"))
    util.rename_xmlid(cr, *eb("hr_recruitment_skills.hr_{candidate,case}_mkt0_skill_softskill_org"))
    util.rename_xmlid(cr, *eb("hr_recruitment_skills.hr_{candidate,case}_mkt1_skill_lang_en"))
    util.rename_xmlid(cr, *eb("hr_recruitment_skills.hr_{candidate,case}_mkt1_skill_lang_fr"))

    util.rename_model(cr, "hr.candidate.skill", "hr.applicant.skill")
    util.create_column(cr, "hr_applicant_skill", "applicant_id", "int4", fk_table="hr_applicant")

    # Update all the existing skills from candidates to either link to the application
    # of a single application candidates or to the talent application in case of multi
    # application candidates
    cr.execute(
        """
        WITH single_application_candidates AS (
            SELECT _upg_orig_candidate_id as candidate_id
              FROM hr_applicant
             WHERE _upg_orig_candidate_id IS NOT NULL
        ), talents AS (
            SELECT hr_applicant_id as id
              FROM hr_applicant_hr_talent_pool_rel
        ), eligible_applicants AS (
            SELECT DISTINCT a.candidate_id,
                   a.id as applicant_id
              FROM hr_applicant a
         LEFT JOIN single_application_candidates sac
                ON a.candidate_id = sac.candidate_id
         LEFT JOIN talents t
                ON a.id = t.id
             WHERE sac.candidate_id IS NOT NULL
                OR t.id IS NOT NULL
        )
        UPDATE hr_applicant_skill has
           SET applicant_id = ea.applicant_id
          FROM eligible_applicants ea
         WHERE has.candidate_id = ea.candidate_id;
        """
    )

    util.remove_field(cr, "hr.applicant.skill", "candidate_id")

    # Duplicate the talents for each applicant that is linked to a talent,
    # so that the talent and all linked applications show the same skills.
    cr.execute("""
       INSERT INTO hr_applicant_skill (
               applicant_id, skill_id, skill_level_id, skill_type_id,
               create_uid, write_uid, create_date, write_date
               )
        SELECT a.id, has.skill_id, has.skill_level_id, has.skill_type_id,
               has.create_uid, has.write_uid, has.create_date, has.write_date
          FROM hr_applicant_skill has
          JOIN hr_applicant a
            ON has.applicant_id = a.pool_applicant_id
    """)
    util.remove_field(cr, "hr.applicant", "candidate_skill_ids")
