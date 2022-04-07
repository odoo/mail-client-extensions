# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # task: 2768677 - removal of the old wizard
    util.remove_model(cr, model="l10n_be_reports.281_50_wizard")
    util.remove_record(cr, "l10n_be_reports.menu_action_report_partner_281_50")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_be_reports.view_partner_281{,_}50_required_fields"))
