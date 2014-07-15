# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # As openerp verify each inherited view as they are create/updated,
    # if a module create more than one inherited view, even the
    # not-updated-yet view are checked. Deleting it to avoitd that.
    util.remove_record(cr, 'account_voucher.view_bank_statement_form_voucher')
