# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company comp
           SET l10n_fr_reference_leave_type = %s
          FROM res_partner part
          JOIN res_country coun ON part.country_id = coun.id
         WHERE comp.partner_id = part.id
           AND coun.id = %s
        """,
        [
            util.ref(cr, "hr_holidays.holiday_status_cl"),
            util.ref(cr, "base.fr"),
        ],
    )
