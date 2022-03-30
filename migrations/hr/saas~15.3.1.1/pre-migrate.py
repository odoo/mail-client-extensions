# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
            DELETE FROM hr_department_mail_channel_rel hdmc
                  USING mail_channel mc
                  WHERE hdmc.mail_channel_id = mc.id
                    AND mc.channel_type != 'channel'
        """
    )

    util.remove_field(cr, "hr.job", "state")
