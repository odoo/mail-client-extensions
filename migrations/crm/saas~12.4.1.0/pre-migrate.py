# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_lead", "automated_probability", "float8")
    util.create_column(cr, "crm_lead", "phone_state", "varchar")
    util.create_column(cr, "crm_lead", "email_state", "varchar")
    # 🏓 field gone in saas~12.1, back in saas~12.3 and removed again in saas~12.4
    util.remove_field(cr, "crm.lead", "partner_address_mobile")

    util.create_column(cr, "crm_stage", "is_won", "boolean")
    cr.execute("UPDATE crm_stage SET is_won=TRUE WHERE probability>=100")
    util.remove_field(cr, "crm.stage", "probability")
    util.remove_field(cr, "crm.stage", "on_change")
    util.remove_field(cr, "res.config.settings", "module_crm_phone_validation")

    # For historical reasons, there's some Lost stages that should not exist anymore...
    # https://www.odoo.com/web#id=1925439&model=project.task&view_type=form&menu_id=
    lost_stage_ids = [s for s in [util.ref(cr, "crm.stage_lead7"), util.ref(cr, "crm.stage_lead8")] if s]

    if lost_stage_ids:
        cr.execute("SELECT id FROM crm_stage WHERE id NOT IN %s ORDER BY sequence,id LIMIT 1", [tuple(lost_stage_ids)])
        first_stage_id = cr.fetchone()[0]
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
