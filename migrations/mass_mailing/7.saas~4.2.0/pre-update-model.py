# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _create_stages(cr):
    stages = 'Schedule Design Sent'.split()
    result = {}

    if util.table_exists(cr, 'mail_mass_mailing_stage'):
        cr.execute("""SELECT name, id
                        FROM mail_mass_mailing_stage
                       WHERE name IN %s
                   """, (stages,))
        result = dict(cr.fetchall())
    else:
        cr.execute("""CREATE TABLE mail_mass_mailing_stage (
                        id serial,
                        name varchar,
                        sequence integer,
                        PRIMARY KEY(id)
                      )
                    """)
        for idx, name in enumerate(stages, 1):
            cr.execute("""INSERT INTO mail_mass_mailing_stage
                                      (name, sequence)
                               VALUES (%s, %s)
                            RETURNING id
                       """, (name, idx * 10))
            [sid] = cr.fetchone()
            result[name] = sid
            name = 'campaign_stage_%d' % idx
            cr.execute("""INSERT INTO ir_model_data
                                      (module, name, model, res_id, noupdate)
                               VALUES (%s, %s, %s, %s, %s)
                       """, ('mass_mailing', name, 'mail.mass_mailing.stage', sid, True))

    return result

def migrate(cr, version):
    stages = _create_stages(cr)

    util.create_column(cr, 'mail_mass_mailing_campaign', 'stage_id', 'int4')
    cr.execute("""UPDATE mail_mass_mailing_campaign c
                     SET stage_id = CASE WHEN EXISTS(SELECT 1
                                                       FROM mail_mail_statistics
                                                      WHERE mass_mailing_campaign_id = c.id
                                                        AND mail_mail_id IS NOT NULL)
                                         THEN %s
                                         ELSE %s
                                    END
                   WHERE stage_id IS NULL
               """, (stages['Sent'], stages['Schedule']))

    # update mail_mass_mailing
    util.create_column(cr, 'mail_mass_mailing', 'state', 'varchar')
    util.create_column(cr, 'mail_mass_mailing', 'email_from', 'varchar')
    util.create_column(cr, 'mail_mass_mailing', 'mailing_model', 'varchar')
    util.create_column(cr, 'mail_mass_mailing', 'body_html', 'text')
    util.create_column(cr, 'mail_mass_mailing', 'reply_to_mode', 'varchar')
    util.create_column(cr, 'mail_mass_mailing', 'reply_to', 'varchar')

    cr.execute("""UPDATE mail_mass_mailing
                     SET email_from = t.email_from,
                         mailing_model = t.model,
                         body_html = t.body_html,
                         reply_to = t.reply_to
                    FROM email_template t
                   WHERE t.id = template_id
               """)

    default_from = """
            SELECT CASE WHEN a.alias_name IS NOT NULL AND c.value IS NOT NULL
                        THEN p.name || ' <' || a.alias_name || '@' || c.value || '>'
                        WHEN p.email IS NOT NULL
                        THEN p.name || ' <' || p.email || '>'
                        ELSE 'noreply@' || current_database()
                    END
              FROM res_users u LEFT JOIN ir_config_parameter c
                                      ON c.key = 'mail.catchall.domain'
                               JOIN mail_alias a
                                 ON a.id = u.alias_id
                               JOIN res_partner p
                                 ON p.id = u.partner_id
             WHERE u.id = coalesce(m.create_uid, 1)
    """

    cr.execute("""UPDATE mail_mass_mailing m
                     SET email_from=(%s)
                   WHERE email_from IS NULL
               """ % default_from)

    cr.execute("""UPDATE mail_mass_mailing m
                     SET reply_to=(%s)
                   WHERE reply_to IS NULL
               """ % default_from)

    cr.execute("UPDATE mail_mass_mailing SET mailing_model=%s WHERE mailing_model IS NULL",
               ('mail.mass_mailing.contact',))

    cr.execute("""UPDATE mail_mass_mailing
                     SET reply_to_mode = CASE WHEN mailing_model IN %s
                                              THEN 'email'
                                              ELSE 'thread'
                                          END
                   WHERE reply_to_mode IS NULL
               """, (('res.partner', 'mail.mass_mailing.contact'),))

    cr.execute("""UPDATE mail_mass_mailing m
                     SET state = CASE WHEN EXISTS(SELECT 1
                                                    FROM mail_mail_statistics
                                                   WHERE mass_mailing_id = m.id)
                                      THEN 'sent'
                                      ELSE 'draft'
                                  END
                   WHERE state IS NULL
               """)

    # update mail_mail_statistics
    cr.execute("""UPDATE mail_mail_statistics s
                     SET mail_mail_id = NULL
                   WHERE NOT EXISTS(SELECT 1
                                      FROM mail_mail
                                     WHERE id = s.mail_mail_id)
               """)
    util.create_column(cr, 'mail_mail_statistics', 'scheduled', 'timestamp without time zone')
    util.create_column(cr, 'mail_mail_statistics', 'sent', 'timestamp without time zone')

    cr.execute("""UPDATE mail_mail_statistics s
                     SET scheduled = s.create_date,
                         sent = m.date
                    FROM mail_mail m
                   WHERE m.id = s.mail_mail_id
               """)
