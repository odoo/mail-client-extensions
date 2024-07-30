def migrate(cr, version):
    cr.execute(
        """
        UPDATE whatsapp_template
           SET template_type = 'marketing'
         WHERE template_type is NULL
        """
    )
