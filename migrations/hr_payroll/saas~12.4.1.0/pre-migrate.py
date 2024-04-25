from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, "hr_contract", "schedule_pay")   # now a related

    # ### resource.calendar
    util.create_column(cr, "resource_calendar", "hours_per_week", "float8")
    cr.execute("""
        WITH sums AS (
            SELECT calendar_id, SUM(hour_to - hour_from) AS hours
              FROM resource_calendar_attendance
          GROUP BY calendar_id
        )
        UPDATE resource_calendar c
           SET hours_per_week = sums.hours
          FROM sums
         WHERE sums.calendar_id = c.id
    """)

    # ### work.entry.type
    if util.table_exists(cr, "hr_work_entry_type"):
        util.create_column(cr, "hr_work_entry_type", "is_unforeseen", "boolean")
        util.create_column(cr, "hr_work_entry_type", "is_leave", "boolean")
        cr.execute("UPDATE hr_work_entry_type SET is_unforeseen = false")
        cr.execute("UPDATE hr_work_entry_type SET code = md5(id::varchar) WHERE code IS NULL")
        # deduplicate entry type on code
        cr.execute("""
            SELECT array_agg(id ORDER BY id)
              FROM hr_work_entry_type
          GROUP BY code
            HAVING count(id) > 1
        """)
        duplicates = {}
        for first, *dups in cr.fetchall():
            duplicates.update({d: first for d in dups})
        if duplicates:
            util.replace_record_references_batch(cr, duplicates, "hr.work.entry.type")
            cr.execute("DELETE FROM hr_work_entry_type WHERE id IN %s", [tuple(duplicates)])
    else:
        # will be needed later for migrating `hr.payslip.worked_days`
        cr.execute("""
            CREATE TABLE hr_work_entry_type(
                id SERIAL NOT NULL PRIMARY KEY,
                create_uid integer,
                create_date timestamp without time zone,
                write_uid integer,
                write_date timestamp without time zone,
                name varchar,
                code varchar,
                sequence int4,
                color int4,
                active boolean,
                is_leave boolean,
                is_unforeseen boolean
            )
        """)

    # structure
    util.create_column(cr, "hr_payroll_structure", "use_worked_day_lines", "boolean")
    util.create_column(cr, "hr_payroll_structure", "schedule_pay", "varchar")
    cr.execute("UPDATE hr_payroll_structure SET use_worked_day_lines = true")

    if util.table_exists(cr, "hr_payroll_structure_type"):
        # new in saas-12.3
        util.create_column(cr, "hr_payroll_structure_type", "country_id", "int4")
        cr.execute("""
            UPDATE hr_payroll_structure s
               SET schedule_pay = t.default_schedule_pay
              FROM hr_payroll_structure_type t
             WHERE s.type_id = t.id
        """)

    # ### hr.payslip.input[.type]
    util.create_column(cr, "hr_payslip_input", "input_type_id", "int4")
    cr.execute("""
        CREATE TABLE hr_payslip_input_type(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            name varchar NOT NULL,
            code varchar NOT NULL,
            country_id integer
        )
    """)
    cr.execute("""
        INSERT INTO hr_payslip_input_type(name, code)
             SELECT name, code
               FROM hr_payslip_input
           GROUP BY name, code
    """)
    cr.execute("""
        UPDATE hr_payslip_input i
           SET input_type_id = t.id
          FROM hr_payslip_input_type t
         WHERE t.code = i.code
           AND t.name = i.name
    """)

    # ### hr.payslip.worked_days
    util.create_column(cr, "hr_payslip_worked_days", "work_entry_type_id", "int4")
    util.create_column(cr, "hr_payslip_worked_days", "amount", "numeric")

    cr.execute("""
        UPDATE hr_payslip_worked_days w
           SET work_entry_type_id = t.id
          FROM hr_work_entry_type t
         WHERE t.code = w.code
           AND work_entry_type_id IS NULL
    """)
    # Create any missing entry type.
    cr.execute("""
        INSERT INTO hr_work_entry_type(name, code, sequence,
                                       color, active, is_leave, is_unforeseen)
             SELECT (array_agg(name))[1], code, min(sequence),
                    0, true, false, false
               FROM hr_payslip_worked_days
              WHERE work_entry_type_id IS NULL
           GROUP BY code
    """)
    cr.execute("""
        UPDATE hr_payslip_worked_days w
           SET work_entry_type_id = t.id
          FROM hr_work_entry_type t
         WHERE t.code = w.code
           AND work_entry_type_id IS NULL
    """)

    if util.table_exists(cr, "hr_payroll_structure_hr_work_entry_type_rel"):
        cr.execute("""
            UPDATE hr_payslip_worked_days w
               SET amount = 0
              FROM hr_payslip p
             WHERE amount IS NULL
               AND p.id = w.payslip_id
               -- AND the entry type is unpaid (in p.struct_id.unpaid_work_entry_type_ids)
               AND EXISTS(SELECT 1
                            FROM hr_payroll_structure_hr_work_entry_type_rel
                           WHERE hr_work_entry_type_id = w.work_entry_type_id
                             AND hr_payroll_structure_id = p.struct_id)
        """)
        # paid amount will be computed in end- (using ORM)

    util.remove_column(cr, "hr_payslip_worked_days", "name")    # now related
    util.remove_column(cr, "hr_payslip_worked_days", "code")    # idem

    # force menu update
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate = false
         WHERE module = 'hr_payroll'
           AND model = 'ir.ui.menu'
    """)

    util.remove_column(cr, "hr_payslip_input", "name")
    util.remove_column(cr, "hr_payslip_input", "code")
