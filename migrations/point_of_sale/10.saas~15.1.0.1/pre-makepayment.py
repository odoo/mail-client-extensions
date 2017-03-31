# -*- coding: utf-8 -*-

def migrate(cr, version):
    # delete all rows from transient model to allow correct creation of new required field
    cr.execute("DELETE FROM pos_make_payment")
