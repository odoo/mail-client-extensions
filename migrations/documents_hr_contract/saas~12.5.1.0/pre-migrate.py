# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("documents{,_hr_contract}.documents_hr_documents_contracts"))
