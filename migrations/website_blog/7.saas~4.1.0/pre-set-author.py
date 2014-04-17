# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'blog_post', 'author_id', 'int4')
    cr.execute("""UPDATE blog_post p
                     SET author_id = u.partner_id
                    FROM res_users u
                   WHERE u.id = p.create_uid
               """)
