def migrate(cr, version):
    cr.execute(
        r"""
        UPDATE mailing_mailing
           SET body_arch = regexp_replace(body_arch, '\yo_mail_wrapper_td\y', 'o_mail_wrapper_td o_editable')
         WHERE body_arch !~ 'o_editable'
        """
    )
