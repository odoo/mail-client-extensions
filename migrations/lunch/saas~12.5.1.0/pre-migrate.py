# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "lunch_location", "company_id", "int4")
    util.create_column(cr, "lunch_alert", "mode", "varchar")
    util.create_column(cr, "lunch_alert", "recipients", "varchar")
    util.create_column(cr, "lunch_alert", "notification_time", "float8")
    util.create_column(cr, "lunch_alert", "notification_moment", "varchar")
    util.create_column(cr, "lunch_alert", "tz", "varchar")

    cr.execute(
        """
        UPDATE lunch_alert a
           SET mode = 'alert',
               recipients = 'everyone',
               notification_time = 10.0,
               notification_moment = 'am',
               tz = p.tz
          FROM res_users u
    INNER JOIN res_partner p ON u.partner_id=p.id
         WHERE u.id = COALESCE(a.write_uid, a.create_uid)
    """
    )
    cr.execute("UPDATE lunch_alert SET tz = 'UTC' WHERE tz IS NULL")

    util.remove_record(cr, "lunch.action_server_lunch_archive_product")
