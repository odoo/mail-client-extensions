# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("14.0"):
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
                "data_merge.data_merge_field_{}_{}".format(model, field),
                "data_merge.rule",
                {
                    "model_id": util.ref(cr, "data_merge.data_merge_model_{}".format(model)),
                    "field_id": util.ref(cr, "base.field_{}__{}".format(model, field)),
                },
            )
            util.force_noupdate(cr, "data_merge.data_merge_field_{}_{}".format(model, field), noupdate=False)

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
