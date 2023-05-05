# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "l10n_be_hr_contract_salary.l10n_be_transport_company_car", util.update_record_from_xml)
