# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "website_calendar.menu_appointment")
    cr.execute(
        """
            UPDATE website_menu
               SET url = '/calendar'
             WHERE url = '/website/calendar'
        """
    )
