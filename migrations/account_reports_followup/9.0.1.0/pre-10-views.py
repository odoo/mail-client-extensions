# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="account_reports_followup.view_partner_inherit_followup_form")
