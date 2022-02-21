# -*- coding: utf-8 -*-


def migrate(cr, version):

    cr.execute(
        """
            DELETE FROM hr_department_mail_channel_rel hdmc
                  USING mail_channel mc
                  WHERE hdmc.mail_channel_id = mc.id
                    AND mc.channel_type != 'channel'
        """
    )
