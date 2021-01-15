# -*- coding: utf-8 -*-

from odoo.tools import html_escape, is_html_empty

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "use_ticket")
    util.remove_field(cr, "event.type", "use_mail_schedule")
    util.remove_field(cr, "event.type", "use_timezone")

    # Since we are removing the event badge customization fields
    # (badge_innerleft, badge_innerright, badge_front, badge_back).
    # Let's be nice and add a message into the migration report for each event record that had those
    # fields (or at least one) configured with a value.
    # That way the end user can try to recover his custom report and include it in the origin event
    # within our new badge report layout.
    cr.execute(
        """
        SELECT name, badge_innerleft, badge_innerright, badge_front, badge_back
          FROM event_event
         WHERE badge_innerleft IS NOT NULL
            OR badge_innerright IS NOT NULL
            OR badge_front IS NOT NULL
            OR badge_back IS NOT NULL
    """
    )
    events_with_customized_badge_report = cr.dictfetchall()
    badge_fields = ["badge_innerleft", "badge_innerright", "badge_front", "badge_back"]
    if events_with_customized_badge_report:
        event_messages = []
        for event_with_customized_badge_report in events_with_customized_badge_report:
            if all([is_html_empty(event_with_customized_badge_report.get(field)) for field in badge_fields]):
                # HTML editor sometimes populate HTML fields with empty HTML (e.g: '<p></p>')
                # if all badge report customization fields are empty, ignore this record
                continue

            event_message = "<span>Event Name: %s</span><br/>" % html_escape(event_with_customized_badge_report["name"])
            for field in badge_fields:
                if not is_html_empty(event_with_customized_badge_report.get(field)):
                    content = html_escape(event_with_customized_badge_report[field])
                    event_message += f"<details><summary>{field}</summary><code>{content}</code></details>"
            event_messages.append(event_message)

        if event_messages:
            util.add_to_migration_reports(
                category="Events",
                message="".join(
                    [
                        "<p>",
                        "<span>While upgrading your database, we found that some content on your customized event ",
                        "badge reports could be lost, following a rework of this report layout.</span><br/>",
                        "<span>Here below is a list of all the impacted events, please make sure that the new event badge ",
                        "report layout suits your needs:</span><br/>",
                        "</p>",
                        "<div>%s</div>",
                    ]
                )
                % ("<br/>".join(event_messages)),
                format="html",
            )

    util.remove_field(cr, "event.event", "badge_innerleft")
    util.remove_field(cr, "event.event", "badge_innerright")
    util.remove_field(cr, "event.event", "badge_front")
    util.remove_field(cr, "event.event", "badge_back")
    util.remove_field(cr, "event.event", "event_logo")

    util.create_column(cr, "event_type", "note", "text")
    util.create_column(cr, "event_type", "ticket_instructions", "text")
    util.create_column(cr, "event_event", "ticket_instructions", "text")

    # move the M2O field `template_id` to the new reference field `template_ref`
    for table_name in ["event_mail", "event_type_mail"]:
        # Remove inconsistent records from the database
        cr.execute(
            f"""
        DELETE FROM {table_name}
              WHERE notification_type = 'mail'
                AND template_id IS NULL
         """,
        )

        util.create_column(cr, table_name, "template_ref", "varchar")

        cr.execute(
            f"""
        UPDATE {table_name}
           SET template_ref = CONCAT('mail.template,', template_id)
         WHERE notification_type = 'mail'
         """,
        )
        model_name = util.model_of_table(cr, table_name)
        util.remove_field(cr, model_name, "template_id")

    util.remove_view(cr, "event.event_registration_report_template_badge")
    util.remove_view(cr, "event.event_event_report_template_badge")

    util.remove_record(cr, "event.report_event_registration_badge")
    util.delete_unused(cr, "event.paperformat_euro_lowmargin")

    util.rename_xmlid(
        cr, "event.report_event_registration_badge", "event.action_report_event_registration_foldable_badge"
    )
