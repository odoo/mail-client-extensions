# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_config_parameter
           SET key='auth_signup.invitation_scope',
               value = CASE WHEN lower(value) = 'true' THEN 'b2c' ELSE 'b2b' END
         WHERE key='auth_signup.allow_uninvited'
    """)
