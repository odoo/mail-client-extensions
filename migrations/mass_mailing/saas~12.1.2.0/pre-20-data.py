# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("mass_mailing.{view_mail_mass_mailing_links,link_tracker_view}_search"))
    util.rename_xmlid(
        cr, *eb("mass_mailing.{action_view_mass_mailing_links_statistics,link_tracker_action_mass_mailing}")
    )
