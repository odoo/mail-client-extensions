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
                cr.mogrify(util.format_query(cr, "{} = %s", column), [bool(keys_to_update.get(key))]).decode()
                for key, column in presence_parameters.items()
            ]
        )

        cr.execute(util.format_query(cr, "UPDATE res_company SET {}", util.SQLStr(set_clause)))

    # explicitly remove the xmlid.
    util.remove_record(cr, "hr.hr_presence_control_login")
