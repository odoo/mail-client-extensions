def migrate(cr, version):
    # Propagate the parent action's groups to its child actions
    # This is only relevant  for the dbs that were already upgraded to saas~18.2
    # without odoo/upgrade@aeb4665c07b942244966adb0a5878142f55f0bf5
    query = """
         WITH child_actions AS (
             SELECT a.id, a.parent_id
               FROM ir_act_server a
               JOIN ir_model_data d
                 ON d.model = 'ir.actions.server'
                AND d.res_id = a.parent_id
              WHERE d.module = 'documents_account'
                AND d.name IN (
                       'ir_actions_server_create_vendor_bill',
                       'ir_actions_server_create_vendor_refund',
                       'ir_actions_server_create_customer_invoice',
                       'ir_actions_server_create_credit_note',
                       'ir_actions_server_create_misc_entry',
                       'ir_actions_server_bank_statement'
                )
         ),
         _del AS (
             DELETE FROM ir_act_server_group_rel r
                   USING child_actions c
                   WHERE r.act_id = c.id
               RETURNING 1
         )
         INSERT INTO ir_act_server_group_rel(act_id, gid)
              SELECT c.id, r.gid
                FROM child_actions c
                JOIN ir_act_server_group_rel r
                  ON r.act_id = c.parent_id, _del
            GROUP BY c.id, r.gid
    """
    cr.execute(query)
