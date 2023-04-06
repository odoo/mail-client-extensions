# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO mail_blacklist (email, active)
             SELECT lower(substring(email_from, '([^ ,;<@]+@[^> ,;]+)')), true
               FROM crm_lead
              WHERE opt_out = true
                AND coalesce(substring(email_from, '([^ ,;<@]+@[^> ,;]+)'), '') != ''
        ON CONFLICT DO NOTHING
    """
    )
    util.update_field_usage(cr, "crm.lead", "opt_out", "is_blacklisted")
    util.remove_field(cr, "crm.lead", "opt_out")
