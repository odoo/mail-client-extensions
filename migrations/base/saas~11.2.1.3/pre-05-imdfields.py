# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # for databases born before 9.0, some cleanup should be made
    util.remove_field(cr, 'account_followup.followup', 'followup_line')
    util.import_script('account_reports_followup/9.0.1.0/pre-20-models.py').migrate(cr, version)
    cr.execute("""
        SELECT array_agg(id ORDER BY id)
          FROM ir_model_fields
         WHERE model = 'account.cashbox.line'
           AND name IN ('number', 'subtotal')
      GROUP BY name
        HAVING count(*) > 1
    """)
    dupes = {x: f[0][0] for f in cr.fetchall() for x in f[0][1:]}
    if dupes:
        util.replace_record_references_batch(cr, dupes, "ir.model.fields", replace_xmlid=False)
        for d in dupes:
            util.remove_record(cr, ("ir.model.fields", d))

    cr.execute("DROP INDEX IF EXISTS ir_model_data_module_name_index")  # old duplicated index
    cr.execute("DROP INDEX IF EXISTS ir_model_data_module_name_uniq_index")  # will be recreated later
    cr.execute("""
        DELETE FROM ir_model_data WHERE id IN (
             SELECT d.id
               FROM ir_model_data d
          LEFT JOIN ir_model_fields f ON (f.id = d.res_id)
              WHERE d.model='ir.model.fields'
                AND f.id IS NULL
        )
    """)

    # some previous migration left ir_model_fields with non existing model name
    # that would crash with the next queries, so we need to clean them up
    cr.execute("""
        DELETE FROM ir_model_fields WHERE model IN (
            'ir.actions.url',
            'email_template.account',
            'res.partner.canal',
            'crm.case',
            'mailgate.thread',
            'mailgate.message'
        )
    """)
    # Remove duplicates...
    cr.execute("""
        DELETE FROM ir_model_data WHERE id IN (
            SELECT unnest((array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)])
              FROM ir_model_data
             WHERE model = 'ir.model.fields'
          GROUP BY module, res_id
            HAVING count(id) > 1
        )
    """)
    cr.execute(r"""
        UPDATE ir_model_data d
           SET name = CONCAT('field_', replace(f.model, '.', '_'), '__', f.name)
          FROM ir_model_fields f
         WHERE d.model='ir.model.fields'
           AND d.res_id = f.id
           AND d.name LIKE 'field\_%'
    """)
