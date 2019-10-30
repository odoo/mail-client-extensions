# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("contacts_enterprise.{contact_map_view,res_partner_view_map}"))
    util.rename_xmlid(cr, *eb("contacts_enterprise.{action_contacts_map_view,res_partner_action_contacts_view_map}"))
