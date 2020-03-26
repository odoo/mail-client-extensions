# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.fixup_m2m(cr, "event_event_tag_rel", "event_event", "event_tag", "event_id", "tag_id")
