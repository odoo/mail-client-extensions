# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "private_street", "varchar")
    util.create_column(cr, "hr_employee", "private_street2", "varchar")
    util.create_column(cr, "hr_employee", "private_city", "varchar")
    util.create_column(cr, "hr_employee", "private_state_id", "int4")
    util.create_column(cr, "hr_employee", "private_zip", "varchar")
    util.create_column(cr, "hr_employee", "private_country_id", "int4")
    util.create_column(cr, "hr_employee", "private_phone", "varchar")
    util.create_column(cr, "hr_employee", "private_email", "varchar")
    util.create_column(cr, "hr_employee", "lang", "varchar")

    util.explode_execute(
        cr,
        """
            UPDATE hr_employee e
               SET
                    private_street = p.street,
                    private_street2 = p.street2,
                    private_city = p.city,
                    private_state_id = p.state_id,
                    private_zip = p.zip,
                    private_country_id = p.country_id,
                    private_phone = p.phone,
                    private_email = p.email,
                    lang = p.lang
              FROM res_partner p
             WHERE e.address_home_id = p.id
        """,
        table="hr_employee",
        alias="e",
    )

    util.explode_execute(
        cr,
        """
            UPDATE res_partner p
               SET active = false
              FROM hr_employee e
             WHERE p.id = e.address_home_id
        """,
        table="res_partner",
        alias="p",
    )

    util.remove_field(cr, "hr.employee", "address_home_id", drop_column=False)
    util.remove_field(cr, "res.users", "address_home_id")

    util.remove_field(cr, "hr.employee", "is_address_home_a_company")
    util.remove_field(cr, "res.users", "is_address_home_a_company")

    util.rename_field(cr, "hr.employee", "phone", "private_phone")
    util.rename_field(cr, "res.users", "employee_phone", "private_phone")

    util.remove_field(cr, "res.partner", "employees_count")

    util.remove_field(cr, "hr.employee.base", "related_contacts_count")
    util.remove_field(cr, "hr.employee.base", "related_contact_ids")
    util.remove_field(cr, "hr.employee.public", "related_contact_ids")

    util.remove_field(cr, "hr.departure.wizard", "archive_private_address")
    util.remove_field(cr, "res.users", "employees_count")

    util.remove_view(cr, "hr.view_employee_form_smartbutton")

    util.explode_execute(
        cr,
        """
            UPDATE hr_employee e
               SET work_contact_id = p.id
              FROM res_partner p
              JOIN res_users u
                ON u.partner_id = p.id
             WHERE e.user_id = u.id
               AND e.work_contact_id IS NULL
               AND e.active = true
        """,
        table="hr_employee",
        alias="e",
    )

    Partner = util.env(cr)["res.partner"]
    cr.execute(
        """
            SELECT
                   work_email,
                   name AS employee_name,
                   id AS employee_id
              FROM hr_employee
             WHERE work_contact_id IS NULL
               AND work_email IS NOT NULL
        """
    )
    for work_email, employee_name, employee_id in cr.fetchall():
        partner = Partner.find_or_create(f"{employee_name} <{work_email}>", assert_valid_email=False)
        cr.execute("UPDATE hr_employee SET work_contact_id = %s WHERE id = %s", [partner.id, employee_id])
