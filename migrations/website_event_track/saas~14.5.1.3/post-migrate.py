# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "website_event_track.mail_template_data_track_confirmation", util.update_record_from_xml)
