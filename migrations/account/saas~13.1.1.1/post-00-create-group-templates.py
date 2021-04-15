# -*- coding: utf-8 -*-
import json

from odoo.upgrade import util


def migrate(cr, version):
    chart_templates = {
        "l10n_ar": util.ref(cr, "l10n_ar.l10nar_base_chart_template"),
        "l10n_do": util.ref(cr, "l10n_do.do_chart_template"),
        "l10n_es": util.ref(cr, "l10n_es.account_chart_template_common"),
        "l10n_pe": util.ref(cr, "l10n_pe.pe_chart_template"),
    }

    no_chart = [k for k, v in chart_templates.items() if not v]
    cr.execute("DELETE FROM ir_model_data WHERE model = 'account.group' AND module = ANY(%s)", [no_chart])

    # cleanup gone xmlids
    cr.execute("DELETE FROM ir_model_data WHERE module = 'l10n_ar' AND name = 'account_group_otros_creditos'")

    cr.execute(
        """
        INSERT INTO account_group_template(id, name, code_prefix_start, chart_template_id)
             SELECT g.id, g.name, g.code_prefix_start, (%s::jsonb->>x.module)::int4
               FROM account_group g
               JOIN ir_model_data x ON (x.model = 'account.group' AND x.res_id = g.id)
              WHERE x.module IN %s
    """,
        [json.dumps(chart_templates), tuple(chart_templates)],
    )

    cr.execute(
        """
        UPDATE ir_model_data
           SET model = 'account.group.template',
               noupdate = false
         WHERE model = 'account.group'
           AND module IN %s
    """,
        [tuple(chart_templates)],
    )

    cr.execute("SELECT GREATEST(max(id), 0) + 1 FROM account_group_template")
    cr.execute("ALTER SEQUENCE account_group_template_id_seq RESTART WITH %s", cr.fetchone())
