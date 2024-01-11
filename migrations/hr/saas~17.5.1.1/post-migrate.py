from ast import literal_eval

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        DELETE
          FROM ir_config_parameter
         WHERE key IN (
            'hr.hr_presence_control_login',
            'hr_presence.hr_presence_control_email',
            'hr_presence.hr_presence_control_ip'
        )
        RETURNING key, value
        """
    )
    rows = cr.fetchall()
    keys_to_update = {row[0]: literal_eval(row[1]) for row in rows}

    presence_parameters = {
        "hr.hr_presence_control_login": "hr_presence_control_login",
        "hr_presence.hr_presence_control_email": "hr_presence_control_email",
        "hr_presence.hr_presence_control_ip": "hr_presence_control_ip",
    }

    if keys_to_update:
        set_clause = ", ".join(
            [
                f"{column} = {'TRUE' if keys_to_update.get(key) else 'FALSE'}"
                for key, column in presence_parameters.items()
            ]
        )

        cr.execute(f"UPDATE res_company SET {set_clause}")

    # explicitly remove the xmlid.
    util.remove_record(cr, "hr.hr_presence_control_login")
