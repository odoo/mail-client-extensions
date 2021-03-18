# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Clean the ACLs XMLID
    acl_name_changes = {
        "event_portal": "event",
        "registration": "registration_user",
        "registration_all": "registration",
        "mail": "mail_user",
        "type_mail_event_manager": "type_mail_manager",
        "category_manager": "tag_category_manager",
        "tag": "tag_user",
    }
    for old_name, new_name in acl_name_changes.items():
        util.rename_xmlid(cr, f"event.access_event_{old_name}", f"event.access_event_{new_name}")

    # event communication upgrade
    util.create_column(cr, "event_mail", "mail_count_done", "integer")

    # registration-based scheduler: count of event_mail_registration sent
    cr.execute(
        """
    WITH mail_grouped_count AS (
          SELECT scheduler_id,
                 count(*) as nbr
            FROM event_mail_registration
           WHERE mail_sent IS TRUE
        GROUP BY scheduler_id)
    UPDATE event_mail em
       SET mail_count_done = mail_gc.nbr
      FROM mail_grouped_count mail_gc
     WHERE em.interval_type = 'after_sub'
       AND mail_gc.scheduler_id=em.id
    """
    )
    # event-based scheduler: number of registrations (update only if already done
    # as indicated by mail_sent)
    cr.execute(
        """
    WITH reg_grouped_count AS (
          SELECT event_id,
                 count(*) as nbr
            FROM event_registration
           WHERE state in ('confirm','done')
        GROUP BY event_id)
    UPDATE event_mail em
       SET mail_count_done = reg_gc.nbr
      FROM reg_grouped_count reg_gc
     WHERE reg_gc.event_id = em.event_id
       AND em.mail_sent IS TRUE
       AND em.interval_type != 'after_sub'
    """
    )

    # rename done to mail_done and redirect old mail_sent on it to have a single "done" field
    util.rename_field(cr, "event.mail", "done", "mail_done")
    util.update_field_references(cr, "mail_sent", "mail_done", only_models=("event.mail",))
    util.remove_field(cr, "event.mail", "mail_sent")
