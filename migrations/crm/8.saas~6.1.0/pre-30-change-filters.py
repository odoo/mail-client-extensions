# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_filters
           SET domain = regexp_replace(domain, '\ycateg_ids\y', 'tag_ids', 'g')
           WHERE model_id = 'crm.lead'
    """)
    if util.table_exists(cr, 'mail_mass_mailing'):
        cr.execute("""
            UPDATE mail_mass_mailing
               SET mailing_domain = regexp_replace(mailing_domain, '\ycateg_ids\y', 'tag_ids', 'g')
             WHERE mailing_model='crm.lead'
               AND mailing_domain IS NOT NULL
        """)
