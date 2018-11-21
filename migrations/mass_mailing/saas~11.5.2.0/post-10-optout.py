# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE mail_mass_mailing_contact_list_rel m
           SET opt_out = p.opt_out,
               unsubscription_date = p.unsubscription_date
          FROM mail_mass_mailing_contact p
         WHERE m.contact_id = p.id
    """
    )
    util.remove_column(cr, "mail_mass_mailing_contact", "opt_out")
    util.remove_column(cr, "mail_mass_mailing_contact", "unsubscription_date")
