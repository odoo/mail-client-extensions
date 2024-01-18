from odoo.upgrade import util


def migrate(cr, version):
    # “cancel” and “open” states relate to calls generated from activities,
    # which no longer exist after the refactoring.
    util.explode_execute(cr, "DELETE FROM voip_phonecall WHERE state IN ('open', 'cancel')", table="voip_phonecall")

    util.create_column(cr, "voip_phonecall", "end_date", "timestamp")
    util.explode_execute(
        cr,
        """
      UPDATE voip_phonecall
         SET mobile = COALESCE(mobile, phone),
             end_date = call_date + duration * interval '1 minute',
             state = CASE WHEN state IN ('done', 'pending') THEN 'terminated' ELSE state END
        """,
        table="voip_phonecall",
    )

    # Delete useless fields, mostly no longer relevant activity integration stuff.
    fields_to_delete = [
        "activity_id",  # activity-related
        "date_deadline",  # activity-related
        "mail_message_id",  # activity-related
        "note",  # activity-related
        "in_queue",  # call queue now directly based on overdue activities
        "sequence",  # call queue now directly based on overdue activities
        "start_time",  # looks like it was not used at all??
        "duration",  # now computed on the client-side from {start,end}_date
        "phone",  # merged with “mobile” into a single field
    ]
    for field in fields_to_delete:
        util.remove_field(cr, "voip.phonecall", field)
    util.remove_field(cr, "mail.activity", "voip_phonecall_id")

    views_to_delete = [
        "voip.view_voip_case_phonecalls_filter",
        "voip.voip_phonecall_tree_view",
    ]
    for view in views_to_delete:
        util.remove_view(cr, view)

    models_to_delete = [
        "voip.phonecall.report",
        "voip.phonecall.log.wizard",
    ]
    for model in models_to_delete:
        util.remove_model(cr, model)

    rename_table = [
        ("call_date", "start_date"),
        ("mobile", "phone_number"),
        ("name", "activity_name"),
    ]
    for old_name, new_name in rename_table:
        util.rename_field(cr, "voip.phonecall", old_name, new_name)
    util.rename_model(cr, "voip.phonecall", "voip.call")
    util.rename_xmlid(cr, "voip.access_voip_phonecall_manager", "voip.access_voip_call_admin")
    util.rename_xmlid(cr, "voip.access_voip_phonecall_user", "voip.access_voip_call_user")

    util.remove_menus(cr, [util.ref(cr, "voip.menu_voip_phonecall_view")])
    util.remove_record(cr, "voip.voip_phonecall_view")
    util.remove_record(cr, "voip.action_add_to_call_queue")
