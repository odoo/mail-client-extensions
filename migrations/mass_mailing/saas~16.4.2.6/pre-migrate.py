# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mass_mailing.mass_mailing_kpi_link_trackers", util.update_record_from_xml)
