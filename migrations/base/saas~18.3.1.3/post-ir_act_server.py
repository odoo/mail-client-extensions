def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_act_server s
           SET html_value = value,
               value = NULL
          FROM ir_model_fields imf
         WHERE imf.id = s.update_field_id
           AND imf.ttype = 'html'
           AND s.value IS NOT NULL
           AND s.html_value IS NULL
        """
    )
