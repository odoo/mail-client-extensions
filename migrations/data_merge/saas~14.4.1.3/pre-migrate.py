# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_model", "ref_merge_ir_act_server_id", "int4")
    util.create_column(cr, "data_merge_model", "is_contextual_merge_action", "boolean", default=False)

    merge_model_rules = [
        ("res_partner", "name"),
        ("res_partner", "vat"),
        ("res_partner", "email"),
        ("res_partner", "ref"),
        ("res_partner_category", "name"),
        ("res_partner_industry", "name"),
        ("res_partner_industry", "full_name"),
        ("res_country", "name"),
    ]
    for model, field in merge_model_rules:
        util.ensure_xmlid_match_record(
            cr,
            f"data_merge.data_merge_field_{model}_{field}",
            "data_merge.rule",
            {
                "model_id": util.ref(cr, f"data_merge.data_merge_model_{model}"),
                "field_id": util.ref(cr, f"base.field_{model}__{field}"),
            },
        )
        util.force_noupdate(cr, f"data_merge.data_merge_field_{model}_{field}", noupdate=False)
    util.ensure_xmlid_match_record(
        cr,
        "data_merge.data_merge_field_res_country_state",
        "data_merge.rule",
        {
            "model_id": util.ref(cr, "data_merge.data_merge_model_res_country_state"),
            "field_id": util.ref(cr, "base.field_res_country_state__name"),
        },
    )
    util.force_noupdate(cr, "data_merge.data_merge_field_res_country_state", noupdate=False)
