# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_m2m(cr, 'mail_mass_mailing_contact_list_rel',
                    'mail_mass_mailing_contact', 'mail_mass_mailing_list',
                    'contact_id', 'list_id')

    cr.execute("""
        INSERT INTO mail_mass_mailing_contact_list_rel(contact_id, list_id)
             SELECT id, list_id FROM mail_mass_mailing_contact
    """)

    util.update_field_usage(cr, 'mail.mass_mailing.contact', 'list_id', 'list_ids')
    util.remove_field(cr, 'mail.mass_mailing.contact', 'list_id')

    util.create_column(cr, 'mail_mass_mailing', 'color', 'int4')
    cr.execute("""
        UPDATE mail_mass_mailing m
           SET color = c.color
          FROM mail_mass_mailing_campaign c
         WHERE c.id = m.mass_mailing_campaign_id
    """)
