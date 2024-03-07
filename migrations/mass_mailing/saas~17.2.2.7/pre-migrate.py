# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mass_mailing.mailing_mailing_view_form_full_width")
    util.remove_record(cr, "mass_mailing.mailing_mailing_action_mail_fullwidth_form")

    util.remove_view(cr, "mass_mailing.view_mail_mass_mailing_graph")
    util.remove_record(cr, "mass_mailing.mailing_mailing_action_mail_fullwidth_graph")
