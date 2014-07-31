# -*- coding: utf-8 -*-

def migrate(cr, version):
    # res.users.signature is now an html fields

    cr.execute("""UPDATE res_users
                     SET signature=CONCAT('<p>', REPLACE(signature, E'\n', '<br>'), '</p>')
                   WHERE signature IS NOT NULL
               """)
