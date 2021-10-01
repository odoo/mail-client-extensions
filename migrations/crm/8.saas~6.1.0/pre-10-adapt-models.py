# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def _move_categ(cr, src_model, new_model, update_m2o):
    cr.execute("SELECT id FROM ir_model WHERE model=%s", [src_model])
    [src_model_id] = cr.fetchone() or [None]
    if not src_model_id or not util.table_exists(cr, util.table_of_model(cr, src_model)):
        return
    new_table = util.table_of_model(cr, new_model)
    cr.execute(
        """CREATE TABLE {table}(
                    id SERIAL NOT NULL PRIMARY KEY,
                    name varchar,
                    team_id integer,
                    _cat_id integer
                  )
               """.format(
            table=new_table
        )
    )
    cr.execute(
        """INSERT INTO {table}(name, team_id, _cat_id)
                       SELECT         name, section_id, id
                         FROM crm_case_categ
                        WHERE object_id = %s
               """.format(
            table=new_table
        ),
        [src_model_id],
    )

    cr.execute("SELECT id FROM ir_model WHERE model=%s", [new_model])
    if not cr.rowcount:
        cr.execute("INSERT INTO ir_model(model, name, state) VALUES (%s, %s, 'base')", [new_model, new_model])

    for tbl, col in update_m2o.items():
        cr.execute("ALTER TABLE {tbl} DROP CONSTRAINT {tbl}_{col}_fkey".format(tbl=tbl, col=col))
        cr.execute(
            """UPDATE {tbl} t
                         SET {col}=c.id
                        FROM {new_table} c
                       WHERE t.{col} = c._cat_id
                   """.format(
                new_table=new_table, tbl=tbl, col=col
            )
        )

    cr.execute("SELECT _cat_id, id FROM {t}".format(t=new_table))
    for o, n in cr.fetchall():
        util.replace_record_references(cr, ("crm.case.categ", o), (new_model, n))


def _new_m2m(cr, old_m2m, new_m2m, tbl1, col1, old_col2, new_col2, new_table):
    if not util.table_exists(cr, old_m2m):
        return
    util.create_m2m(cr, new_m2m, tbl1, new_table, col1, new_col2)
    cr.execute(
        """
        INSERT INTO {new_m2m}({col1}, {new_col2})
             SELECT o.{col1}, n.id
               FROM {old_m2m} o
               JOIN {new_table} n
                 ON o.{old_col2} = n._cat_id
    """.format(
            **locals()
        )
    )

    # XXX check all values copied?
    cr.execute("DROP TABLE {0}".format(old_m2m))


def migrate(cr, version):
    util.drop_depending_views(cr, "crm_stage", "type")
    util.drop_depending_views(cr, "crm_phonecall", "priority")

    util.rename_model(cr, "crm.case.stage", "crm.stage")
    util.delete_model(cr, "crm.payment.mode")
    util.delete_model(cr, "crm.segmentation")
    util.delete_model(cr, "crm.segmentation.line")

    cr.execute("ALTER TABLE section_stage_rel RENAME TO crm_team_stage_rel")
    cr.execute("ALTER TABLE crm_team_stage_rel RENAME COLUMN section_id TO team_id")

    # force update message subtypes that use `section_id`
    for suffix in ["", "_stage", "_won", "_lost"]:
        util.force_noupdate(cr, "crm.mt_salesteam_lead" + suffix, False)

    reports = "categ2 stage categ.stage categ.categ2".split()
    for r in reports:
        old = "report.crm.case.section." + r
        new = "report.crm.team." + r
        util.rename_model(cr, old, new, rename_table=False)
        cr.execute("DROP VIEW IF EXISTS {0}".format(util.table_of_model(cr, old)))

    xids = {
        "crm.crm_case_section_act_tree": "crm.crm_team_act_tree",
        "crm.crm_case_section_salesteams_view_kanban": "crm.crm_team_salesteams_view_kanban",
        "crm.crm_case_stage_tree": "crm.crm_stage_tree",
        "crm.crm_case_stage_form": "crm.crm_stage_form",
        "crm.crm_case_stage_act": "crm.crm_stage_act",
        "crm.crm_case_category_act_leads_all": "crm.crm_lead_all_leads",
        "crm.crm_case_category_act_oppor11": "crm.crm_lead_opportunities",
        "crm.crm_lead_categ_action": "crm.crm_lead_tag_action",
        "crm.crm_case_categ_phone0": "crm.crm_phonecall_category_phone0",
        "crm.crm_case_categ_phone_incoming0": "crm.crm_phonecall_category_phone_incoming0",
        "crm.crm_case_categ_phone_outgoing0": "crm.crm_phonecall_category_phone_outgoing0",
        "crm.crm_phonecall_categ_action": "crm.crm_phonecall_category_action",
    }

    # reports views use the same pattern for xmlid data
    reports[0] = "categ"  # but use a different name from this report
    for r in reports:
        u = r.replace(".", "_")
        for t in "tree form graph filter".split():
            old = "crm.view_crm_case_section_{0}_{1}".format(u, t)
            new = "crm.view_crm_team_{0}_{1}".format(u, t)
            xids[old] = new
        old = "crm.action_report_crm_case_section_{0}_tree".format(u)
        new = "crm.action_report_crm_team_{0}_tree".format(u)
        xids[old] = new

    for f, t in xids.items():
        util.rename_xmlid(cr, f, t)

    # crm.case.categ has been split in multiple specific tables
    _move_categ(cr, "crm.lead", "crm.lead.tag", {})
    _new_m2m(
        cr, "crm_lead_category_rel", "crm_lead_tag_rel", "crm_lead", "lead_id", "category_id", "tag_id", "crm_lead_tag"
    )
    # m2m from `sale_crm` module
    _new_m2m(
        cr,
        "sale_order_category_rel",
        "sale_order_tag_rel",
        "sale_order",
        "order_id",
        "category_id",
        "tag_id",
        "crm_lead_tag",
    )

    _move_categ(
        cr,
        "crm.phonecall",
        "crm.phonecall.category",
        {
            "crm_phonecall": "categ_id",
            "crm_phonecall2phonecall": "categ_id",
        },
    )
    # from other modules, but MUST be done here because we will drop the old table
    _move_categ(
        cr,
        "crm.claim",
        "crm.claim.category",
        {
            "crm_claim": "categ_id",
        },
    )
    _move_categ(
        cr,
        "crm.helpdesk",
        "crm.helpdesk.category",
        {
            "crm_helpdesk": "categ_id",
        },
    )

    # cleanup
    for t in ["crm_lead_tag", "crm_phonecall_category", "crm_claim_category", "crm_helpdesk_category"]:
        if util.table_exists(cr, t):
            cr.execute("ALTER TABLE {0} DROP COLUMN _cat_id".format(t))

    util.delete_model(cr, "crm.case.categ")
