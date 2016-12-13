# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # bootstrap warn fields on partners
    cr.execute("""
        ALTER TABLE res_partner
         ADD COLUMN invoice_warn varchar,
         ADD COLUMN invoice_warn_msg text,
         ADD COLUMN sale_warn varchar,
         ADD COLUMN sale_warn_msg text,
         ADD COLUMN picking_warn varchar,
         ADD COLUMN picking_warn_msg text,
         ADD COLUMN purchase_warn varchar,
         ADD COLUMN purchase_warn_msg text
    """)
    cr.execute("""
        UPDATE res_partner
           SET invoice_warn = 'no-message',
               sale_warn = 'no-message',
               picking_warn = 'no-message',
               purchase_warn = 'no-message'
    """)
    cr.execute("""
        ALTER TABLE res_partner
       ALTER COLUMN invoice_warn SET NOT NULL,
       ALTER COLUMN sale_warn SET NOT NULL,
       ALTER COLUMN picking_warn SET NOT NULL,
       ALTER COLUMN purchase_warn SET NOT NULL
    """)

def _db_watermark_collection(cr, version):
    util.remove_view(cr, view_id=823)
    cr.execute("UPDATE ir_ui_view SET inherit_id=610 WHERE inherit_id=800")

def _db_tvpaint(cr, version):
    cr.execute("UPDATE ir_ui_view SET priority=42 WHERE id=832")

def _db_houtmerk(cr, version):
    cr.execute("UPDATE ir_ui_view SET inherit_id=633 WHERE id=2491")

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '05a64ced-5b98-488d-a833-a994f9b1dd80': _db_openerp,    # test
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,    # prod
        '3dc91671-94e5-4018-9f14-6251c822e93b': _db_watermark_collection,
        '454555a6-d931-47a9-bc25-bbc11dab3a67': _db_tvpaint,
        'ce2bbc1f-5d81-4140-909e-1204e9f743b7': _db_houtmerk,
    })
