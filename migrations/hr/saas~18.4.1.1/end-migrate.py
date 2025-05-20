from datetime import datetime

from odoo.upgrade import util


def migrate(cr, version):
    # For each employee without a contract, create a version with values filled in from the employee fields
    common_fields = util.get_common_columns(cr, "hr_employee", "hr_version", ignore=("id", "active"))
    common_fields = util.ColumnList.from_unquoted(cr, common_fields)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    root_id = util.ref(cr, "base.user_root")
    required_default_values = [
        ("hr_responsible_id", root_id),
        ("last_modified_uid", root_id),
        ("last_modified_date", now_str),
    ]
    # hr_work_entry
    if util.column_exists(cr, "hr_version", "work_entry_source"):
        required_default_values.append(("work_entry_source", "calendar"))
        # Dummy default values are ok for date_generated_from/to, if they are
        # equal they are reset on the first work entries generation to avoid
        # generating records on large period
        required_default_values.append(("date_generated_from", now_str))
        required_default_values.append(("date_generated_to", now_str))
    # l10n_lu_hr_payroll
    if util.column_exists(cr, "hr_version", "l10n_lu_meal_voucher_employee_computation"):
        required_default_values.append(("l10n_lu_meal_voucher_employee_computation", "removed_from_net"))
    # l10n_mx_hr_payroll
    if util.column_exists(cr, "hr_version", "l10n_mx_schedule_pay"):
        required_default_values.append(("l10n_mx_schedule_pay", "monthly"))
        required_default_values.append(("l10n_mx_payment_period_vouchers", "last_day_of_month"))

    required_fields = util.ColumnList.from_unquoted(cr, [e[0] for e in required_default_values])
    required_values = util.SQLStr(", ".join(["%s" for _ in required_default_values]))
    util.env(cr)["hr.employee"].search([("version_id", "=", False)])

    query = util.format_query(
        cr,
        """
        WITH insert_versions AS (
            INSERT INTO hr_version (
                        employee_id, date_version, active,
                        {required_fields},
                        {common_fields})
                 SELECT e.id AS employee_id, DATE(e.create_date) AS date_version, TRUE AS active,
                        {required_values},
                        {common_fields_aliased}
                   FROM hr_employee e
                  WHERE e.current_version_id IS NULL
              RETURNING id, employee_id
        )
        UPDATE hr_employee e
           SET current_version_id = v.id
          FROM insert_versions v
         WHERE e.id = v.employee_id
        """,
        required_values=required_values,
        required_fields=required_fields,
        common_fields=common_fields,
        common_fields_aliased=common_fields.using(alias="e"),
    )
    cr.execute(query, [e[1] for e in required_default_values])

    util.make_field_non_stored(cr, "hr.employee", "private_street", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "private_street2", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "private_city", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "private_state_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "private_zip", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "private_country_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "country_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "marital", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "spouse_complete_name", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "spouse_birthdate", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "children", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "ssnid", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "identification_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "passport_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "distance_home_work", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "km_home_work", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "distance_home_work_unit", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "employee_type", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "notes", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "departure_reason_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "departure_description", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "departure_date", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "resource_calendar_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "department_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "job_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "address_id", selectable=True)
    util.make_field_non_stored(cr, "hr.employee", "work_location_id", selectable=True)

    util.make_field_non_stored(cr, "hr.employee", "version_id")
