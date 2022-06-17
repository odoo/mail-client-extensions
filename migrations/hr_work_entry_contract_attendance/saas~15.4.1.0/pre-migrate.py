# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{planning_contract,hr_work_entry_contract_attendance}.hr_contract_hne"))
