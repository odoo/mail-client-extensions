def migrate(cr, version):
    cr.execute(
        """
        WITH gone_fields AS (
            DELETE FROM ir_model_fields
                  WHERE model = 'ir_actions_account_report_download'
                    AND name NOT IN ('id', 'display_name', '__last_update')
              RETURNING id
            )
        DELETE FROM ir_model_data
              USING gone_fields
              WHERE res_id = gone_fields.id
                AND model = 'ir.model.fields'
        """
    )
