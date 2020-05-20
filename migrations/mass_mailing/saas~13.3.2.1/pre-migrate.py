# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mailing_mailing", "lang", "varchar")

    for field in "clicks_ratio items clicked".split():
        util.remove_field(cr, "utm.campaign", f"mailing_{field}")
    for field in "total scheduled failed ignored sent delivered opened replied bounced".split():
        util.remove_field(cr, "utm.campaign", field)

    # data
    eb = util.expand_braces
    for view in "search form tree kanban pivot graph".split():
        util.rename_xmlid(cr, *eb(f"mass_mailing.{{view_mail_mass_mailing_contact,mailing_contact_view}}_{view}"))

    util.remove_record(cr, "mass_mailing.link_tracker_action_mass_mailing")
    util.remove_record(cr, "mass_mailing.link_tracker_action_mass_mailing_campaign")
