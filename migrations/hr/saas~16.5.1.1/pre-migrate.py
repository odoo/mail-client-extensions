from odoo.addons.base.maintenance.migrations.util import table_exists
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment"):
        util.move_field_to_module(cr, "hr.employee", "newly_hired_employee", "hr_recruitment", "hr")
        util.rename_field(cr, "hr.employee", "newly_hired_employee", "newly_hired")

    util.create_column(cr, "hr_contract_type", "code", "varchar")

    util.explode_execute(
        cr,
        "UPDATE hr_contract_type SET code = name->>'en_US'",
        table="hr_contract_type",
    )

    util.move_field_to_module(cr, "hr.departure.reason", "reason_code", "l10n_be_hr_payroll", "hr")

    cr.execute(
        """
    SELECT id
      FROM ir_model
     WHERE model = 'hr.employee'
        """
    )
    [model_id] = cr.fetchone()

    util.create_column(
        cr, "mail_activity_plan", "department_id", "int4", fk_table="hr_department", on_delete_action="CASCADE"
    )
    util.create_column(cr, "mail_activity_plan", "_old_id", "int4")
    cr.execute(
        """
    INSERT INTO mail_activity_plan (
                _old_id, company_id, department_id, create_uid, write_uid, name,
                res_model_id, res_model, active, create_date, write_date)
         SELECT id, company_id, department_id, create_uid, write_uid, name,
                %s, 'hr.employee', active, create_date, write_date
           FROM hr_plan
      RETURNING _old_id, id
        """,
        [model_id],
    )
    id_map = dict(cr.fetchall())
    if id_map:
        util.replace_record_references_batch(cr, id_map, model_src="hr.plan", model_dst="mail.activity.plan")

    util.create_column(cr, "mail_activity_plan_template", "_old_id", "int4")
    if util.module_installed(cr, "hr_contract_sign"):
        util.create_column(
            cr,
            "mail_activity_plan_template",
            "sign_template_id",
            "int4",
            fk_table="sign_template",
            on_delete_action="SET NULL",
        )
        util.create_column(
            cr,
            "mail_activity_plan_template",
            "employee_role_id",
            "int4",
            fk_table="sign_item_role",
            on_delete_action="SET NULL",
        )
        add_columns = util.ColumnList.from_unquoted(cr, ["sign_template_id", "employee_role_id"])
    else:
        add_columns = util.ColumnList()

    query = util.format_query(
        cr,
        """
    INSERT INTO mail_activity_plan_template (
                _old_id, activity_type_id, responsible_id, plan_id, create_uid, write_uid,
                summary, responsible_type, note, create_date, write_date {}
                )
         SELECT old.id, old.activity_type_id, old.responsible_id, new_plan.id, old.create_uid, old.write_uid,
                old.summary, old.responsible, old.note, old.create_date, old.write_date {}
           FROM hr_plan_activity_type AS old
           JOIN mail_activity_plan AS new_plan ON new_plan._old_id = old.plan_id
      RETURNING _old_id, id
            """,
        add_columns.using(leading_comma=True),
        add_columns.using(leading_comma=True, alias="old"),
    )
    cr.execute(query)
    id_map = dict(cr.fetchall())
    if id_map:
        util.replace_record_references_batch(
            cr, id_map, model_src="hr.plan.activity.type", model_dst="mail.activity.plan.template"
        )
    util.remove_column(cr, "mail_activity_plan", "_old_id")
    util.remove_column(cr, "mail_activity_plan_template", "_old_id")

    if table_exists(cr, "hr_plan_employee_activity"):  # introduced in 16.2
        query = cr.mogrify(
            """
            UPDATE mail_activity AS activity
               SET res_model = 'hr.employee',
                   res_model_id = %s,
                   res_id = original_record.employee_id,
                   res_name = employee.name
              FROM hr_plan_employee_activity AS original_record
              JOIN hr_employee AS employee
                ON employee.id = original_record.employee_id
             WHERE activity.res_model_id = %s
               AND original_record.id = activity.res_id
            """,
            [
                util.ref(cr, "hr.model_hr_employee"),
                util.ref(cr, "hr.model_hr_plan_employee_activity"),
            ],
        ).decode()
        util.explode_execute(cr, query, table="hr_plan_employee_activity", alias="original_record")

    util.remove_model(cr, "hr.plan.activity.type")
    util.remove_model(cr, "hr.plan.employee.activity")
    util.remove_model(cr, "hr.plan")
    util.remove_model(cr, "hr.plan.wizard")
    util.remove_view(cr, "hr.mail_activity_type_form_inherit")
