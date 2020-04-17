# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.fixup_m2m(cr, "calendar_event_res_partner_rel", "calendar_event", "res_partner")

    # Default value for newly required fields
    cr.execute("UPDATE calendar_event SET privacy = 'private' WHERE privacy IS NULL")
    cr.execute("UPDATE calendar_event SET show_as = 'busy' WHERE show_as IS NULL")
