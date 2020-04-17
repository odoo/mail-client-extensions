# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE slide_channel SET completed_template_id = %s
        """,
        [util.ref(cr, "website_slides.mail_template_channel_completed")],
    )
