# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_job", "published_date", "date")

    cr.execute(
        """
            UPDATE hr_job
               SET published_date = write_date::date
             WHERE is_published = true
        """
    )
