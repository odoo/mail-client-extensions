from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_recruitment.{candidate,applicant}_hired_template"))
    util.if_unchanged(cr, "hr_recruitment.applicant_hired_template", util.update_record_from_xml)

    util.create_column(cr, "hr_applicant", "availability", "date")
    util.create_column(cr, "hr_applicant", "color", "integer")
    util.create_column(cr, "hr_applicant", "email_from", "character varying(128)")
    util.create_column(cr, "hr_applicant", "email_normalized", "character varying")
    util.create_column(cr, "hr_applicant", "employee_id", "integer")
    util.create_column(cr, "hr_applicant", "linkedin_profile", "character varying")
    util.create_column(cr, "hr_applicant", "partner_id", "integer")
    util.create_column(cr, "hr_applicant", "partner_name", "character varying")
    util.create_column(cr, "hr_applicant", "partner_phone", "character varying(32)")
    util.create_column(cr, "hr_applicant", "partner_phone_sanitized", "character varying")
    util.create_column(cr, "hr_applicant", "type_id", "integer")
    util.create_column(cr, "hr_applicant", "pool_applicant_id", "integer")
    # Temporary column to mark which candidates only have a single application
    util.create_column(cr, "hr_applicant", "_upg_orig_candidate_id", "integer")

    # Some terminology to hopefully make this migration a bit easier to understand
    # ---
    # Before migration:
    #
    # hr.candidate -> A model that is meant to represent a person. This model contains all the contact information such as
    #                 name, phone, email etc. A candidate/person can apply to multiple jobs within the same company
    # hr.applicant -> A model that is meant to represent one application to one job position by one candidate, Most of
    #                 the information on this model, such as the contact information, is related fields from the candidate
    #                 so the actual applicant model does not contain that much information.
    #
    # Note:
    # - A candidate can have 0, 1, or multiple applications.
    # - An application can NOT have multiple candidates.
    # - An application can only be for ONE job position.
    #
    # ---
    # After migration:
    #
    # hr.candidate -> Removed.
    # hr.applicant -> Now it holds all the contact information about a person(all the previously related fields from
    #                 candidate) as well as an application to a single job position.
    # hr.talent.pool -> A way to group or collect applications together. Similar to a how a job groups together all
    #                   the applications that are applying for that job, or how the tag "developer" groups together all
    #                   the "developer" applications.
    #
    # Notes:
    # - An application that is linked to a talent pool (often referred to as a talent here) is NOT linked to any job position.
    # - Similarly an applicant that is linked to a job position (normal application) should NOT be linked to a talent pool.
    # - One could view talents as 'template applications' for a specific human so when a talent applies for a new job position
    #   the talent record is duplicated, talent_pool_ids is removed from the duplicate and a job_id added.
    # - Therefor it is vital that we don't add existing applications to a talent pool and rather create new ones.
    # - One talent record can belong to many talent pools (m2m relationship).
    #
    # ---
    # The general strategy for the migration can be explained as such:
    # 1. If candidate has only 1 application
    #     - Move info(phone, email, etc.) from candidate to applicant
    #     - Move notes/chatter to applicant
    #     - Move activities to applicant
    #     - Move meetings to applicant
    # 2. If candidate has != 1 application
    #     - Create a talent pool with the name 'Candidates'
    #     - Create a new applicant (talent)
    #     - Move all information and references from the candidate to the newly created talent
    #     - link the talent to the talent pool 'Candidates'
    #     - Link all the applications from the candidate to the new applicant(talent) through pool_applicant_id
    #     - Copy info(phone, email, etc.) from the candidate/talent to all the linked applications.
    #     - Copy/duplicate skills from the candidate to all the linked applications, including the talent.
    #
    # The idea behind this twofold strategy is to try to minimize clutter in customers databases. If most, or all, of the
    # candidates only have a single application, it can be interpreted that the customer did not utilize the candidate
    # mechanism in any useful manner (managing multiple applications for the same human etc), and therefor it is no need to
    # clutter up the database and set up a talent pool for the candidates. However, if the candidates contain either 0 or
    # more than 1 application it means that the candidate mechanism was properly used and we should do all we can to
    # preserve that behavior (following step 2 of the strategy).

    # Move all the information from the related fields on candidate into applicant
    cr.execute(
        """
        UPDATE hr_applicant a
           SET availability = c.availability,
               color = c.color,
               email_from = c.email_from,
               email_normalized = c.email_normalized,
               employee_id = c.employee_id,
               linkedin_profile = c.linkedin_profile,
               partner_id = c.partner_id,
               partner_name = c.partner_name,
               partner_phone = c.partner_phone,
               partner_phone_sanitized = c.partner_phone_sanitized,
               type_id = c.type_id
          FROM hr_candidate c
         WHERE a.candidate_id = c.id
        """
    )

    # For candidates with only 1 application.
    cr.execute(
        """
        WITH single_application_candidates AS (
            SELECT candidate_id
              FROM hr_applicant
          GROUP BY candidate_id
            HAVING COUNT(id) = 1
        )
        UPDATE hr_applicant a
           SET _upg_orig_candidate_id = a.candidate_id
          FROM single_application_candidates sac
         WHERE a.candidate_id = sac.candidate_id
     RETURNING a.candidate_id,
               a.id AS applicant_id
        """
    )
    candidate_to_applicant_mapping = dict(cr.fetchall())

    # Collect all candidates that have no company_id set and add them to the report.
    cr.execute("""
        SELECT id, partner_name FROM hr_candidate
        WHERE company_id IS NULL
    """)
    candidates_without_company = cr.fetchall()
    if candidates_without_company:
        msg = """
        <details>
        <summary>
        The database contained candidates without a company set.
        This is a invalid configuration and should not exist.
        During the migration an applicant containing all the information from the
        candidate was created but as it will also lack a company it might be difficult to find.
        In order to have correct migrated data you could set a company to each
        the the candidates listed below. Then perform a new upgrade request.
        </summary>
        <ul>{}</ul>
        </details>
        """.format(
            "".join("<li>Candidate: {}, id: {}</li>".format(info[1], info[0]) for info in candidates_without_company)
        )
        util.add_to_migration_reports(msg, category="Recruitment", format="html")

    # Check if there are any candidates with multiple applications indicating that the candidate feature is used
    cr.execute(
        """
            SELECT DISTINCT c.company_id
              FROM hr_candidate c
         LEFT JOIN hr_applicant a
                ON c.id = a.candidate_id
             WHERE c.company_id IS NOT NULL
             GROUP BY c.id
            HAVING COUNT(a.id) <> 1
        """
    )
    cids = tuple(r[0] for r in cr.fetchall())
    if cids:
        cr.execute(
            """
            CREATE TABLE hr_talent_pool (
               id SERIAL NOT NULL PRIMARY KEY,
               active       boolean,
               color        integer,
               company_id   integer,
               create_date  timestamp without time zone,
               create_uid   integer,
               description  text,
               name         character varying,
               pool_manager integer,
               write_date   timestamp without time zone,
               write_uid    integer
            )
            """
        )

        util.create_m2m(cr, "hr_applicant_hr_talent_pool_rel", "hr_applicant", "hr_talent_pool")

        # Create a "Candidates" talent pool for each company
        cr.execute(
            """
            INSERT INTO hr_talent_pool ( active, company_id, description, name )
            SELECT true, id, 'Candidates have been migrated into a talent pool', 'Candidates for company ' || name
              FROM res_company
             WHERE id IN %s
            """,
            [cids],
        )
        extra_columns, extra_values = "", ""
        if util.column_exists(cr, "hr_applicant", "referral_state"):  # from `hr_referral`
            extra_columns = ", referral_state"
            extra_values = ", 'progress'"
        # For candidates with 0 or more than 1 application.
        cr.execute(
            util.format_query(
                cr,
                """
            -- Create an applicant('talent') for each candidate with more or less than 1 applcation
            WITH inserted_applicants AS (
                INSERT
                  INTO hr_applicant (
                           active, availability, candidate_id, color, company_id,
                           create_date, email_from, email_normalized, employee_id,
                           kanban_state, linkedin_profile, partner_id, partner_name,
                           partner_phone, partner_phone_sanitized, priority, type_id,
                           user_id
                           {}
                       )
                SELECT c.active, c.availability, c.id, c.color, c.company_id,
                       c.create_date, c.email_from, c.email_normalized,
                       c.employee_id, 'normal', c.linkedin_profile, c.partner_id,
                       c.partner_name, c.partner_phone, c.partner_phone_sanitized,
                       c.priority, c.type_id, c.user_id
                       {}
                  FROM hr_candidate c
             LEFT JOIN hr_applicant a
                    ON c.id = a.candidate_id
              GROUP BY c.id
                HAVING COUNT(a.id) <> 1
             RETURNING id, company_id, candidate_id
            ),
            -- Link the applications, that were linked to the candidate, to the new talent
            updated_applicants AS (
                UPDATE hr_applicant a
                   SET pool_applicant_id = ia.id
                  FROM inserted_applicants ia
                 WHERE a.candidate_id = ia.candidate_id
            ),
            -- Add the 'talent' to the candidate talent pool
            talent_pool_relations AS (
                INSERT
                  INTO hr_applicant_hr_talent_pool_rel (
                            hr_applicant_id, hr_talent_pool_id
                       )
                SELECT
                       a.id as hr_applicant_id,
                       tp.id as hr_talent_pool_id
                  FROM inserted_applicants a
                  JOIN hr_talent_pool tp
                    ON tp.company_id = a.company_id
            )
            SELECT candidate_id, id
              FROM inserted_applicants
            """,
                util.SQLStr(extra_columns),
                util.SQLStr(extra_values),
            )
        )
        candidate_to_applicant_mapping.update(cr.fetchall())

    if candidate_to_applicant_mapping:
        util.replace_record_references_batch(cr, candidate_to_applicant_mapping, "hr.candidate", "hr.applicant")

        cr.execute(
            """
            WITH duplicates AS (
                SELECT unnest((array_agg(id ORDER BY id))[2:]) AS id
                  FROM ir_attachment
                 WHERE res_model = 'hr.applicant'
              GROUP BY res_id,
                       store_fname
                HAVING count(*) > 1
            )
            DELETE FROM ir_attachment
                  USING duplicates
                  WHERE ir_attachment.id = duplicates.id
            """
        )

    util.remove_field(cr, "calendar.event", "candidate_id")
    util.remove_field(cr, "res.company", "candidate_properties_definition")
    util.remove_field(cr, "hr.employee", "candidate_id")
    util.remove_field(cr, "hr.applicant", "other_applications_count")
    util.remove_field(cr, "hr.applicant", "candidate_id", drop_column=False)
    util.remove_model(cr, "candidate.send.mail")
