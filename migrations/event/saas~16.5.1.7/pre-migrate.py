# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("event.action_report_event_registration{_foldable,}_badge"))
    util.rename_xmlid(cr, *eb("event.action_report_event_event{_foldable,}_badge"))
    util.rename_xmlid(cr, *eb("event.event_event_report_template{_foldable,}_badge"))
    util.rename_xmlid(cr, *eb("event.event_registration_report_template{_foldable,}_badge"))
    util.rename_xmlid(cr, *eb("event.paperformat_event{_foldable,}_badge"))

    util.create_column(cr, "event_event", "badge_format", "varchar", default="A6")
    util.create_column(cr, "event_event_ticket", "color", "varchar", default="#875A7B")
