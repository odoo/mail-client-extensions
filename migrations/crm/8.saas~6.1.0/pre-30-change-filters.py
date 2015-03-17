# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_filters
           SET domain = regexp_replace(domain, '\ycateg_ids\y', 'tag_ids', 'g')
           WHERE model_id = 'crm.lead'
    """)
