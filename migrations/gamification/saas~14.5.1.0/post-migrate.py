# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "gamification.email_template_badge_received", util.update_record_from_xml)
    util.if_unchanged(cr, "gamification.email_template_goal_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "gamification.simple_report_template", util.update_record_from_xml)
    util.if_unchanged(cr, "gamification.mail_template_data_new_rank_reached", util.update_record_from_xml)
