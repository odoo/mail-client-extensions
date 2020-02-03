# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_followup_followup_line", "company_id", "int4")
    util.create_column(cr, "account_followup_followup_line", "sms_description", "varchar")
    util.create_column(cr, "account_followup_followup_line", "send_sms", "boolean")
    util.create_column(cr, "account_followup_followup_line", "join_invoices", "boolean")
    util.create_column(cr, "account_followup_followup_line", "auto_execute", "boolean")

    cr.execute(
        """
        UPDATE account_followup_followup_line l
           SET company_id=f.company_id,
               sms_description='Dear %(partner_name)s, it seems that some of your payments stay unpaid',
               send_sms=FALSE
          FROM account_followup_followup f
         WHERE f.id=l.followup_id
    """
    )

    util.remove_field(cr, "account_followup_followup_line", "sequence")
    util.remove_field(cr, "account_followup_followup_line", "followup_id")
    util.remove_model(cr, "account_followup.followup")
