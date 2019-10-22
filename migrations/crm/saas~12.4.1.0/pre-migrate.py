# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_lead", "automated_probability", "float8")
    util.create_column(cr, "crm_lead", "phone_state", "varchar")
    util.create_column(cr, "crm_lead", "email_state", "varchar")
    util.create_column(cr, "crm_stage", "is_won", "boolean")
    cr.execute("UPDATE crm_stage SET is_won=TRUE WHERE probability>=100")
    util.remove_field(cr, "crm.stage", "probability")
    util.remove_field(cr, "crm.stage", "on_change")
    util.remove_field(cr, "res.config.settings", "module_crm_phone_validation")

    # For historical reasons, there's some Lost stages that should not exist anymore...
    # https://www.odoo.com/web#id=1925439&model=project.task&view_type=form&menu_id=
    lost_stage_ids = [s for s in [util.ref(cr, "crm.stage_lead7"), util.ref(cr, "crm.stage_lead8")] if s]
    cr.execute("select id from crm_stage order by sequence,id limit 1")
    first_stage_id = cr.fetchone()[0]

    if lost_stage_ids:
        cr.execute(
            """
            UPDATE crm_lead
               SET stage_id=%s,
                   probability=0,
                   active=FALSE
             WHERE stage_id in %s
            """,
            [first_stage_id, tuple(lost_stage_ids)],
        )
        util.remove_record(cr, "crm.stage_lead7")
        util.remove_record(cr, "crm.stage_lead8")
