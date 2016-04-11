# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    l10n = 'ae ar at au be bo br ch cl co cr do fr gr gt hn jp lu mx '\
           'no pa pe pl pt ro sa sg si th tr uk uy ve vn'.split()
    for c in l10n:
        util.remove_record(cr, 'l10n_{0}.action_client_l10n_{0}_menu'.format(c))
