from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_appraisal.mail_template_appraisal_{request,reminder}"))

    util.remove_model(cr, "hr.appraisal.report")

    util.remove_field(cr, "res.config.settings", "appraisal_template_id")
    util.remove_field(cr, "res.company", "appraisal_template_id")
    util.remove_field(cr, "hr.employee.base", "last_appraisal_state")
    util.remove_field(cr, "hr.employee", "last_appraisal_date")
    util.remove_field(cr, "hr.appraisal", "last_appraisal_date")
    util.remove_field(cr, "hr.appraisal", "previous_appraisal_date")
    util.remove_field(cr, "hr.appraisal", "manager_user_ids")
    util.remove_field(cr, "hr.department", "custom_appraisal_template_id")
    util.remove_field(cr, "res.users", "next_appraisal_date")

    # Copy the value of hr_appraisal.employee_id.current_version_id.job_id to hr_appraisal.job_id for all records
    util.create_column(cr, "hr_appraisal", "job_id", "int4")
    query = """
        UPDATE hr_appraisal AS a
        SET job_id = v.job_id
        FROM hr_employee as e
        JOIN hr_version as v
        ON e.current_version_id = v.id
        WHERE a.employee_id = e.id
    """
    util.explode_execute(cr, query, table="hr_appraisal", alias="a")
