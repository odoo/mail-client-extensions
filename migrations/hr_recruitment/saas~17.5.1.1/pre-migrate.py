from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_recruitment.{applicant,candidate}_hired_template"))
    util.update_record_from_xml(cr, "hr_recruitment.candidate_hired_template")

    util.rename_field(cr, "hr.applicant", "emp_id", "employee_id")

    cr.execute(
        """
        CREATE TABLE hr_candidate (
            id SERIAL NOT NULL PRIMARY KEY,
            create_uid integer,
            write_uid integer,
            company_id integer,
            partner_id integer,
            type_id integer,
            color integer,
            user_id integer,
            employee_id integer,
            message_bounce integer,
            create_date timestamp without time zone,
            write_date timestamp without time zone,
            active boolean,
            email_from character varying(128),
            partner_phone character varying(32),
            partner_mobile character varying(32),
            phone_sanitized character varying,
            email_normalized character varying,
            email_cc character varying,
            partner_name character varying,
            partner_phone_sanitized character varying,
            partner_mobile_sanitized character varying,
            linkedin_profile character varying,
            priority character varying,
            availability date,
            tmp_applicant_id integer)
        """
    )

    util.create_column(cr, "hr_applicant", "candidate_id", "int4", fk_table="hr_candidate")

    cr.execute(
        """
        INSERT INTO hr_candidate (
            company_id, partner_id, type_id, color, user_id, employee_id, message_bounce,
            active, email_from, partner_phone, partner_mobile, phone_sanitized,
            email_normalized, email_cc, partner_name, partner_phone_sanitized,
            partner_mobile_sanitized, linkedin_profile, availability, priority, tmp_applicant_id
        )
        SELECT
            company_id, partner_id, type_id, color, user_id, employee_id, message_bounce,
            active, email_from, partner_phone, partner_mobile, phone_sanitized,
            email_normalized, email_cc, partner_name, partner_phone_sanitized,
            partner_mobile_sanitized, linkedin_profile, availability, priority, id
        FROM hr_applicant
        """
    )

    # Create temporary index to speed up following requests
    cr.execute("CREATE INDEX _tmp_applicant_id_idx ON hr_candidate(tmp_applicant_id)")

    cr.execute(
        """
        UPDATE hr_applicant
           SET candidate_id = hr_candidate.id
          FROM hr_candidate
         WHERE hr_applicant.id = hr_candidate.tmp_applicant_id
        """
    )

    query = """
        UPDATE ir_attachment a
           SET res_model = 'hr.candidate',
               res_id = hr_candidate.id
          FROM hr_candidate
         WHERE a.res_model = 'hr.applicant'
           AND a.res_id = hr_candidate.tmp_applicant_id
    """
    util.explode_execute(cr, query, table="ir_attachment", alias="a")

    cr.execute("DROP INDEX _tmp_applicant_id_idx")
    cr.execute("ALTER TABLE hr_candidate DROP COLUMN tmp_applicant_id")

    util.create_column(cr, "calendar_event", "candidate_id", "int4")
    query = """
        UPDATE calendar_event e
           SET candidate_id = a.candidate_id
          FROM hr_applicant a
         WHERE e.applicant_id = a.id
    """
    util.explode_execute(cr, query, table="calendar_event", alias="e")

    util.remove_field(cr, "hr.applicant", "message_bounce")
    util.remove_field(cr, "hr.applicant", "application_count")
    util.remove_field(cr, "hr.applicant", "phone_mobile_search")
    util.remove_field(cr, "hr.applicant", "is_blacklisted")
    util.remove_field(cr, "hr.applicant", "mobile_blacklisted")
    util.remove_field(cr, "hr.applicant", "phone_blacklisted")
    util.remove_field(cr, "hr.applicant", "phone_sanitized_blacklisted")
    util.remove_field(cr, "hr.applicant", "phone_sanitized")
    util.remove_field(cr, "hr.applicant", "name")
    util.remove_column(cr, "hr_applicant", "email_from")
    util.remove_column(cr, "hr_applicant", "email_normalized")
    util.remove_column(cr, "hr_applicant", "partner_id")
    util.remove_column(cr, "hr_applicant", "availability")
    util.remove_column(cr, "hr_applicant", "partner_name")
    util.remove_column(cr, "hr_applicant", "partner_phone")
    util.remove_column(cr, "hr_applicant", "partner_phone_sanitized")
    util.remove_column(cr, "hr_applicant", "partner_mobile")
    util.remove_column(cr, "hr_applicant", "partner_mobile_sanitized")
    util.remove_column(cr, "hr_applicant", "type_id")
    util.remove_column(cr, "hr_applicant", "color")
    util.remove_column(cr, "hr_applicant", "linkedin_profile")

    util.remove_field(cr, "hr.employee", "applicant_id")
