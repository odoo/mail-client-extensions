# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE mail_alias SET alias_name=NULL WHERE trim(alias_name) = ''")
