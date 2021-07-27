# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """Remove the pdf processing cron for counting pdf pages of sign/saas~14.5.1.0/post-migrate.py if it has been processed"""
    cron_id = util.ref(cr, "__upgrade__.post_upgrade_process_sign_pdfs")
    if cron_id:
        cr.execute(
            """
            SELECT 1
              FROM ir_cron
             WHERE id = %s
               -- Note: use a negative search to handle the case of NULL values in write/create_date
               AND now() - create_date < interval '1 month'
        """,
            (cron_id,),
        )
        if not cr.rowcount:
            util.remove_record(cr, "__upgrade__.post_upgrade_process_sign_pdfs")
