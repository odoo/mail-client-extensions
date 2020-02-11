# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Removal of twitter hashtag field could lead to crash if not updated
    util.force_noupdate(cr, 'website_event.event_description_full', False)
