# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """Remove the resize images cron of product/saas~12.2.1.2/post-image.py if it has been processed"""
    cron_id = util.ref(cr, "__upgrade__.post_upgrade_resize_image")
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
            util.remove_record(cr, "__upgrade__.post_upgrade_resize_image")
