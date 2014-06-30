# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("DELETE FROM ir_attachment WHERE name=%s AND res_model is null",
               ('invitation.ics',)
               )
