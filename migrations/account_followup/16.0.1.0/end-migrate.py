# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.is_changed(cr, "account_followup.demo_followup_line1"):
        cr.execute(
            """
            DELETE FROM mail_template
             WHERE id = (
               SELECT mail_template_id
                 FROM account_followup_followup_line
                WHERE id = %s
             )
            """,
            [util.ref(cr, "account_followup.demo_followup_line1")],
        )
        util.update_record_from_xml(cr, "account_followup.demo_followup_line1", force_create=False)
