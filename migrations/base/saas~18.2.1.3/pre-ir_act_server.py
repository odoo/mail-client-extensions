from odoo.upgrade import util


def migrate(cr, version):
    # Adding upfront the automated_name column to avoid its computation, because:
    # - there's no point to compute it for existing actions (they already have a name)
    # - compute it when upgrading base module could lead to an error as the compute
    #   method relies on other modules and the registry won't be entirely set up
    util.create_column(cr, "ir_act_server", "automated_name", "varchar")

    # Converting ir_act_server.child_ids field from many2many to one2many type.
    # This means:
    #   - fetch all records from table rel_server_actions (=child_ids as many2many)
    #   - dispatch those records in ir_act_server table by:
    #     - setting parent_id (=child_ids as one2many)
    #     - duplicating them if needed (i.e. has originally more than one parent)
    #     - + also duplicate all their xmlids if they had some

    # `_upg_<something>` columns are removed in `base/saas-18.2.1.3/end-ir_act_server.py`
    util.create_column(cr, "ir_act_server", "_upg_orig_id", "int4")  # keep track of original server action id
    util.create_column(
        cr, "ir_act_server", "_upg_matched", "bool", default=None
    )  # used for xmlid rematching, see related `documents` upgrade scripts
    util.create_column(cr, "ir_act_server", "parent_id", "int4", fk_table="ir_act_server", on_delete_action="CASCADE")
    act_cols = util.get_columns(
        cr,
        "ir_act_server",
        ignore=("id", "_upg_orig_id", "_upg_matched", "parent_id", "base_automation_id"),
    )
    has_studio = util.column_exists(cr, "ir_model_data", "studio")
    query = util.format_query(
        cr,
        """
        WITH aggregated_relations AS (
            -- Aggregate all child_ids many2many values
              SELECT ARRAY_AGG(rsa.server_id ORDER BY (rsa.action_id)) AS parent_ids,
                     rsa.action_id
                FROM rel_server_actions rsa
            GROUP BY rsa.action_id
        ), updated_actions AS (
            -- Update existing actions if they only have a single parent.
               UPDATE ir_act_server ias
                  SET _upg_orig_id = ias.id,
                      parent_id = ar.parent_ids[1]
                 FROM aggregated_relations ar
                WHERE ar.action_id = ias.id
                  AND CARDINALITY(ar.parent_ids) = 1
            RETURNING ias.id
        ), inserted_actions AS (
            -- Duplicate all actions that have more than one parent,
            -- linking only duplicates and leaving original ones as orphans
            INSERT INTO ir_act_server (
                        parent_id,
                        _upg_orig_id,
                        {act_cols}
                      )
                 SELECT UNNEST(ar.parent_ids),
                        ar.action_id,
                        {ias__act_cols}
                   FROM aggregated_relations ar
                   JOIN ir_act_server ias
                     ON ias.id = ar.action_id
                  WHERE CARDINALITY(ar.parent_ids) > 1
              RETURNING id, _upg_orig_id, parent_id
        ), inserted_xmlids AS (
            -- Create similar xmlids for inserted actions (if they had some)
                INSERT INTO ir_model_data (
                            res_id,
                            module,
                            name,
                            model,
                            noupdate
                            {studio_col}
                          )
                     SELECT ins.id,
                            unnest(ARRAY['__upgrade__', '__cloc_exclude__']),
                            CONCAT_WS('__', imd.name, 'copy', ins.parent_id, ins.id),
                            imd.model,
                            imd.noupdate
                            {imd__studio_col}
                       FROM inserted_actions ins
                 INNER JOIN ir_model_data imd
                         ON imd.res_id = ins._upg_orig_id
                      WHERE imd.model = 'ir.actions.server'
                  RETURNING res_id
        )
            -- Dummy query just to make sure all CTEs are executed.
            SELECT ua.id, ix.res_id
              FROM inserted_xmlids ix
              JOIN updated_actions ua
                ON ua.id = ix.res_id
        """,
        act_cols=act_cols,
        ias__act_cols=act_cols.using(alias="ias"),
        studio_col=util.SQLStr(", studio" if has_studio else ""),
        imd__studio_col=util.SQLStr(", imd.studio" if has_studio else ""),
    )
    cr.execute(query)
    # Any action must have *at least* the same groups its parent has
    cr.execute(
        """
        WITH RECURSIVE action_tree AS (
             SELECT act_id, gid
               FROM ir_act_server_group_rel
              UNION
             SELECT a.id as act_id, r.gid
               FROM action_tree r
               JOIN ir_act_server a
                 ON r.act_id = a.parent_id
        )
        INSERT INTO ir_act_server_group_rel(act_id, gid)
             SELECT act_id, gid
               FROM action_tree
        ON CONFLICT DO NOTHING
        """
    )

    # When the same field is changed from m2m to o2m,
    # the relation is not automatically dropped.
    # We then need to drop it manually:
    cr.execute("DROP TABLE IF EXISTS rel_server_actions CASCADE")
    cr.execute(
        "DELETE FROM ir_model_relation r USING ir_model m WHERE m.id = r.model AND r.name = 'rel_server_actions'"
    )


def rematch_xmlids(cr, child_xmlids_changes_by_parent, mute_missing_child=False):
    """
    Now that there is no more the possibility to link a single server action to
    multiple parents, you must have adapted your module's server actions' data.
    Use this helper when you did.

    :param dict child_xmlids_changes_by_parent: shape of dict is the following
        { parent_xlmid: { actual_child_xmlid: original_child_xmlid } }
    :param bool mute_missing_child: if True, skip missing child actions without warning
    """
    for parent_xmlid, child_xmlids_changes in child_xmlids_changes_by_parent.items():
        parent_id = util.ref(cr, parent_xmlid)
        if not parent_id:
            util._logger.warning("Cannot find parent action %s", parent_xmlid)
            continue
        for xmlid, original_xmlid in child_xmlids_changes.items():
            child_id = util.ensure_xmlid_match_record(
                cr,
                xmlid=xmlid,
                model="ir.actions.server",
                values={
                    "_upg_orig_id": util.ref(cr, original_xmlid),
                    "_upg_matched": None,
                    "parent_id": parent_id,
                },
            )

            if not child_id:
                if not mute_missing_child:
                    util._logger.warning("Couldn't find a match for child action %s (parent=%s)", xmlid, parent_xmlid)
                continue

            # Making sure we do not match again the same child action, as a precaution.
            cr.execute("UPDATE ir_act_server SET _upg_matched=TRUE WHERE id=%s", [child_id])

            # Drop temporary xmlid for already matched action
            cr.execute(
                r"""
                DELETE FROM ir_model_data
                      WHERE module IN ('__upgrade__', '__cloc_exclude__')
                        AND model = 'ir.actions.server'
                        AND name LIKE '%%\_\_copy\_\_%s\_\_%s'
                """,
                [parent_id, child_id],
            )
