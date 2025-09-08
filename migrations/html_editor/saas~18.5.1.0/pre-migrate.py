def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_config_parameter
           SET key = CASE key
                         WHEN 'web_editor.olg_api_endpoint' THEN 'html_editor.olg_api_endpoint'
                         ELSE 'html_editor.media_library_endpoint'
                     END
         WHERE key IN ('web_editor.olg_api_endpoint', 'web_editor.media_library_endpoint');
        """
    )
