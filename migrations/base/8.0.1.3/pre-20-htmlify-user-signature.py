# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # res.users.signature is now an html fields

    cr.execute("""UPDATE res_users
                     SET signature={}
                   WHERE signature IS NOT NULL
               """.format(util.pg_text2html('signature')))
