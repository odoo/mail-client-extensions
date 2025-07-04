from odoo.upgrade import util


def move_columns(cr, employee_columns, create_columns=True):
    valid_columns = []
    for col in employee_columns:
        ctype = util.column_type(cr, "hr_employee", col)
        if ctype is None:
            util._logger.error(
                "Cannot move the column `%s` from `hr_employee` to `hr_version` since it doesn't exist", col
            )
            continue
        valid_columns.append(col)
        if create_columns and not util.create_column(cr, "hr_version", col, ctype):
            util._logger.warning("The column `%s` in `hr_version` table already exists", col)

    columns = util.ColumnList.from_unquoted(cr, valid_columns)
    query = util.format_query(
        cr,
        """
        UPDATE hr_version v
           SET ({}) = ROW ({})
          FROM hr_employee e
         WHERE v.employee_id = e.id
           AND {}
        """,
        columns,
        columns.using(alias="e"),
        util.SQLStr("e._upg_existing" if util.column_exists(cr, "hr_employee", "_upg_existing") else "True"),
    )
    cr.execute(query)


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr.ir_rule_hr_contract_manager")
    util.update_record_from_xml(cr, "hr.ir_rule_hr_contract_multi_company")

    columns = [
        "private_street",
        "private_street2",
        "private_city",
        "private_state_id",
        "private_zip",
        "private_country_id",
        "country_id",
        "marital",
        "spouse_complete_name",
        "spouse_birthdate",
        "children",
        "ssnid",
        "identification_id",
        "passport_id",
        "distance_home_work",
        "distance_home_work_unit",
        "km_home_work",
        "employee_type",
        "departure_reason_id",
        "departure_description",
        "departure_date",
        "address_id",
        "work_location_id",
    ]
    move_columns(cr, employee_columns=columns, create_columns=False)
