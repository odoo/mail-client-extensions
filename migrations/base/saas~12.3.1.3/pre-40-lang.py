# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("UPDATE ir_translation SET lang='ar_001' WHERE lang = 'ar_AA' ")
    cr.execute("UPDATE res_lang SET code = 'ar_001' WHERE code = 'ar_AA' ")
    cr.execute("UPDATE res_partner SET lang = 'ar_001' WHERE lang = 'ar_AA' ")
