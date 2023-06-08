# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mass_mailing.mass_mailing_kpi_link_trackers", util.update_record_from_xml)
    util.remove_view(cr, "mass_mailing.iframe_css_assets_readonly")
    util.remove_view(cr, "mass_mailing.iframe_css_assets_edit")
    util.remove_view(cr, "mass_mailing.mass_mailing_mail_style")
