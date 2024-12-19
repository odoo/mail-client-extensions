import logging

from odoo.upgrade import util


def migrate(cr, version):
    log = logging.getLogger("odoo.upgrade.hr.164").info

    log("Initialise new private information columns")
    util.create_column(cr, "hr_employee", "private_street", "varchar")
    util.create_column(cr, "hr_employee", "private_street2", "varchar")
    util.create_column(cr, "hr_employee", "private_city", "varchar")
    util.create_column(cr, "hr_employee", "private_state_id", "int4")
    util.create_column(cr, "hr_employee", "private_zip", "varchar")
    util.create_column(cr, "hr_employee", "private_country_id", "int4")
    util.create_column(cr, "hr_employee", "private_phone", "varchar")
    util.create_column(cr, "hr_employee", "private_email", "varchar")
    util.create_column(cr, "hr_employee", "lang", "varchar")

    log("Copy private information from private addresses to employee forms")
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

    for field in ["street", "street2", "city", "state_id", "zip", "country_id", "phone", "email"]:
        util.update_field_usage(cr, "hr.employee", f"address_home_id.{field}", f"private_{field}")
    util.update_field_usage(cr, "hr.employee", "address_home_id.lang", "lang")

    log("Archive private addresses + make public + empty private information")
    util.explode_execute(
        cr,
        """
            UPDATE res_partner p
               SET
                   active = false,
                   type = 'contact',
                   name = COALESCE(p.name, e.name, e.id::varchar),
                   street = NULL,
                   street2 = NULL,
                   city = NULL,
                   state_id = NULL,
                   zip = NULL,
                   country_id = NULL,
                   phone = NULL,
                   email = NULL
              FROM hr_employee e
             WHERE p.id = e.address_home_id
               AND p.type = 'private'
        """,
        table="res_partner",
        alias="p",
    )

    log("Empty chatter")
    util.explode_execute(
        cr,
        """
            DELETE FROM mail_message m
                  USING res_partner p
                   JOIN hr_employee e
                     ON e.address_home_id = p.id
                  WHERE m.model = 'res.partner'
                    AND m.res_id = p.id
                    AND p.type = 'private'
        """,
        table="mail_message",
        alias="m",
        bucket_size=100_000,
    )

    log("remove old fields")
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

    log("Set user's partner as work contact (if any)")
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

    log("Force work contact creation is not linked to user (if work email)")
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
    for work_email, employee_name, employee_id in util.log_progress(
        cr.fetchall(), util._logger, qualifier="employees", size=cr.rowcount
    ):
        partner = Partner.find_or_create(f"{employee_name} <{work_email}>", assert_valid_email=False)
        cr.execute("UPDATE hr_employee SET work_contact_id = %s WHERE id = %s", [partner.id, employee_id])

    cr.execute("ALTER TABLE res_partner_bank DROP CONSTRAINT IF EXISTS res_partner_bank_unique_number")

    cr.execute(
        """
        UPDATE res_partner_bank b
           SET partner_id = e.work_contact_id
          FROM hr_employee e
         WHERE b.partner_id = e.address_home_id
           AND e.work_contact_id IS NOT NULL
           AND b.partner_id != e.work_contact_id
        """
    )

    # Move bank account from private contact to work contact
    cr.execute(
        """
        WITH dups AS (
             SELECT partner_id,
                    sanitized_acc_number,
                    ARRAY_AGG(id) AS ids
               FROM res_partner_bank
           GROUP BY 1, 2
             HAVING COUNT(*) > 1
        )
        SELECT UNNEST(ids[2:]), ids[1] FROM dups
        """
    )
    mapping = {bank_id[0]: bank_id[1] for bank_id in cr.fetchall() if bank_id[0] != bank_id[1]}

    if mapping:
        util.replace_record_references_batch(cr, mapping, "res.partner.bank", ignores=["mail_followers"])
        util.remove_records(cr, "res.partner.bank", mapping.keys())

    cr.execute(
        "ALTER TABLE res_partner_bank ADD CONSTRAINT res_partner_bank_unique_number UNIQUE (sanitized_acc_number, partner_id)"
    )
