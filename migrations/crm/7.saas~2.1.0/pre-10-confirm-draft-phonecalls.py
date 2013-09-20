# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("UPDATE crm_phonecall SET state=%s WHERE state=%s", ('open', 'draft'))
