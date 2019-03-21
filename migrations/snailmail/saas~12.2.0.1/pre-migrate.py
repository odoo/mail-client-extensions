# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "snailmail_cover ", "boolean")
    util.remove_field(cr, "snailmail.letter", "activity_id")
    util.create_column(cr, "snailmail_letter", "cover", "boolean")
    for f in {"message_id", "state_id", "country_id"}:
        util.create_column(cr, "snailmail_letter", f, "int4")

    for f in {"error_code", "street", "street2", "zip", "city"}:
        util.create_column(cr, "snailmail_letter", f, "varchar")

    cr.execute("UPDATE snailmail_letter SET error_code = 'UNKNOWN_ERROR' WHERE state = 'error'")
    cr.execute("UPDATE snailmail_letter SET state = 'pending' WHERE state = 'draft'")
    cr.execute(
        """
        UPDATE snailmail_letter l
           SET street = p.street,
               street2 = p.street2,
               zip = p.zip,
               city = p.city,
               state_id = p.state_id,
               country_id = p.country_id
          FROM res_partner p
         WHERE p.id = l.partner_id
    """
    )

    util.remove_view(cr, "snailmail.res_config_settings_view_form")
