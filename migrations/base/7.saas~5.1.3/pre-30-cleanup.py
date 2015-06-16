# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # this views is auto-generated when updating res.groups
    util.remove_view(cr, 'base.user_groups_view')

    # change in this view is minimal (c7e68feca83c0ce52fe815e827db3a588facaf9a)
    # removing the view is unnecessary and overkill.
    util.force_noupdate(cr, 'base.view_users_form', False)

    if util.table_exists(cr, 'audittrail_log_line'):
        cr.execute("""
            ALTER TABLE audittrail_log_line
                DROP CONSTRAINT IF EXISTS audittrail_log_line_field_id_fkey;
            ALTER TABLE audittrail_log_line
                ADD CONSTRAINT audittrail_log_line_field_id_fkey
                FOREIGN KEY (field_id)
                REFERENCES ir_model_fields(id)
                ON DELETE CASCADE;
            """)
