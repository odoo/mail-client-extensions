def migrate(cr, version):
    cr.execute("""
        UPDATE ai_composer composer
           SET interface_key = 'html_field_knowledge'
         WHERE composer.name = 'Knowledge Article HTML'
    """)
