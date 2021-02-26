# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            CREATE TABLE IF NOT EXISTS hr_work_location (
                id SERIAL PRIMARY KEY,
                active BOOLEAN,
                name varchar,
                company_id int,
                address_id int,
                create_uid integer,
                create_date timestamp without time zone,
                write_uid integer,
                write_date timestamp without time zone,
                location_number varchar
            )
        """
    )

    util.create_column(cr, "hr_employee", "work_location_id", "int4")

    cr.execute(
        """
            INSERT INTO hr_work_location(name, company_id, address_id, active, create_uid, create_date, write_uid, write_date)
                 SELECT work_location, company_id, address_id, true, 1, now() at time zone 'utc', 1, now() at time zone 'utc'
                   FROM hr_employee
                  WHERE work_location IS NOT NULL
               GROUP BY work_location, company_id, address_id
        """
    )

    cr.execute(
        """
        UPDATE hr_employee empl
           SET work_location_id = wl.id
          FROM hr_work_location wl
         WHERE empl.work_location = wl.name
           AND empl.company_id = wl.company_id
           AND empl.address_id = wl.address_id
        """
    )

    util.remove_field(cr, "res.users", "work_location")
    util.remove_field(cr, "hr.employee.base", "work_location")

    util.create_column(cr, "hr_employee", "departure_reason_id", "int4")
    util.remove_field(cr, "hr.departure.wizard", "departure_reason")
