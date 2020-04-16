# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO mail_blacklist (email, active)
             SELECT lower(substring(email, '([^ ,;<@]+@[^> ,;]+)')), true
               FROM res_partner
              WHERE opt_out = true
                AND coalesce(substring(email, '([^ ,;<@]+@[^> ,;]+)'), '') != ''
        ON CONFLICT DO NOTHING
    """
    )
    util.remove_field(cr, "res.partner", "opt_out")
    util.remove_field(cr, "res.users", "opt_out", drop_column=False)
