from odoo.upgrade import util


def migrate(cr, version):
    default_template = util.ref(cr, "hr_appraisal.hr_appraisal_default_template")

    cr.execute("SELECT count(*) FROM res_company")
    if cr.fetchone()[0] > 1:
        # Create new default templates based on companies
        cr.execute(
            """
            WITH new_tmpl AS (
                INSERT INTO hr_appraisal_template(
                                company_id, description,
                                appraisal_employee_feedback_template,
                                appraisal_manager_feedback_template)
                     SELECT id, 'Default Template (' || name || ')',
                            appraisal_employee_feedback_template,
                            appraisal_manager_feedback_template
                       FROM res_company
                  RETURNING company_id, id
            )
            UPDATE res_company c
               SET appraisal_template_id = new_tmpl.id
              FROM new_tmpl
             WHERE new_tmpl.company_id = c.id
            """
        )
    else:
        # Update appraisal default template for single company
        cr.execute(
            """
            UPDATE hr_appraisal_template AS h
               SET appraisal_employee_feedback_template = c.appraisal_employee_feedback_template,
                   appraisal_manager_feedback_template = c.appraisal_manager_feedback_template
              FROM res_company c
             WHERE h.id = %s;

            UPDATE res_company SET appraisal_template_id = %s;
            """,
            [default_template, default_template],
        )

    util.create_column(cr, "hr_appraisal_template", "__upg_dep_id", "int4")

    cr.execute(
        """
        WITH info AS (
            SELECT d.id AS dep_id,
                   d.name->>'en_US' || ' Template' AS name,
                   d.custom_appraisal_templates,
                   d.employee_feedback_template AS employee_feedback_template,
                   d.manager_feedback_template AS manager_feedback_template,
                   d.company_id,
                   c.appraisal_template_id
              FROM hr_department d
              JOIN res_company c
                ON d.company_id = c.id
        ), new_tmpl AS (
            INSERT INTO hr_appraisal_template(
                            company_id, description,
                            appraisal_employee_feedback_template,
                            appraisal_manager_feedback_template,
                            __upg_dep_id)
                 SELECT i.company_id, i.name,
                        i.employee_feedback_template,
                        i.manager_feedback_template,
                        i.dep_id
                   FROM info i
                  WHERE i.custom_appraisal_templates
              RETURNING id, __upg_dep_id AS dep_id
        )
        UPDATE hr_department d
           SET custom_appraisal_template_id = COALESCE(new_tmpl.id, info.appraisal_template_id, %s)
          FROM info
     LEFT JOIN new_tmpl
            ON info.dep_id = new_tmpl.dep_id
         WHERE d.id = info.dep_id
        """,
        [default_template],
    )

    util.remove_column(cr, "hr_appraisal_template", "__upg_dep_id")
    util.remove_field(cr, "res.company", "appraisal_manager_feedback_template")
    util.remove_field(cr, "res.company", "appraisal_employee_feedback_template")
    util.remove_field(cr, "res.config.settings", "appraisal_manager_feedback_template")
    util.remove_field(cr, "res.config.settings", "appraisal_employee_feedback_template")
    util.remove_field(cr, "hr.department", "employee_feedback_template")
    util.remove_field(cr, "hr.department", "manager_feedback_template")
    util.remove_field(cr, "hr.department", "custom_appraisal_templates")
    util.recompute_fields(cr, "hr.appraisal", ["appraisal_template_id"])
