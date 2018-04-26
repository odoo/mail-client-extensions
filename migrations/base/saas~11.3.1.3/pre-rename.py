# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, 'auth_signup.default_template_user', 'base.template_portal_user_id')
    util.rename_xmlid(cr, *eb('{auth_signup,base}.default_template_user_config'))
    cr.execute("""
        UPDATE ir_config_parameter
           SET key='base.template_portal_user_id'
         WHERE key='auth_signup.template_user_id'
    """)
