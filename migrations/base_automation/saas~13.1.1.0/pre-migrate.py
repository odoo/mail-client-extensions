# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "base_automation_onchange_fields_rel", "base_automation", "ir_model_fields")
    cr.execute("""
        WITH ocf AS (
            SELECT a.id, s.model_id, trim(regexp_split_to_table(a.on_change_fields, ',')) as name
              FROM base_automation a
              JOIN ir_act_server s ON s.id = a.action_server_id
        )
        INSERT INTO base_automation_onchange_fields_rel(base_automation_id, ir_model_fields_id)
             SELECT o.id, f.id
               FROM ocf o
               JOIN ir_model_fields f USING (model_id, name)
        ON CONFLICT DO NOTHING
    """)
    util.remove_field(cr, "base.automation", "on_change_fields")

    # remove test models and linked data
    # They actually have been moved to the new module `test_base_automation` (which is not installed)
    names = util.splitlines("""
        on_create
        on_write
        on_recompute
        recursive
        on_line
        on_write_check_context
        with_trigger
        on_write_recompute_send_email
    """)
    for name in names:
        util.remove_record(cr, f"base_automation.test_rule_{name}")
        util.remove_record(cr, f"base_automation.test_rule_{name}_ir_actions_server")

    util.remove_record(cr, "base_automation.test_mail_template_automation")

    for l_word in "lead line link linked".split():
        util.remove_model(cr, f"base.automation.{l_word}.test")
