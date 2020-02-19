# -*- coding: utf-8 -*-
from itertools import chain

from odoo.addons.base.maintenance.migrations import util
from odoo.exceptions import UserError


def migrate(cr, version):
    india_country_id = util.ref(cr, 'base.in')
    in_other_territory = util.ref(cr, 'l10n_in.state_in_ot')
    delivery_partner_field = 'am.partner_id'
    if util.column_exists(cr, "account_move", "partner_shipping_id"):
        delivery_partner_field = 'COALESCE(am.partner_shipping_id, am.partner_id)'
    #set value in l10n_in_gstin from partner vat where this new give flexibility to enter other state GSTIN number.
    #set value in l10n_in_state_id from state of partner or company unit where product is consumed.
    #set value in l10n_in_gst_treatment from old field in invoice where only defined that what type of export invoice is this new field is support more type
    #we can't use old field because it's have wrong name.
    account_move_update_query = f"""
        WITH
        company_with_l10n_in_coa AS (
            SELECT c.id
            FROM res_company c
            JOIN ir_model_data d ON c.chart_template_id = d.res_id
                AND d.module = 'l10n_in'
                AND d.model = 'account.chart.template'
                AND d.name = 'indian_chart_template_standard')

        UPDATE account_move SET
            l10n_in_gstin = CASE
                WHEN partner.country_id = %s THEN partner.vat
                ELSE NULL
            END,
            l10n_in_state_id = CASE
                WHEN am.commercial_partner_id IS NULL AND journal.type = 'sale' THEN company_unit_partner.state_id
                WHEN delivery_partner.country_id = %s AND journal.type = 'sale' THEN delivery_partner.state_id
                WHEN delivery_partner.country_id != %s AND journal.type = 'sale' THEN %s
                WHEN journal.type = 'purchase' THEN company_unit_partner.state_id
                ELSE NULL
            END,
            l10n_in_gst_treatment = CASE
                WHEN am.l10n_in_export_type IN ('sez_with_igst','sez_without_igst') THEN 'special_economic_zone'
                WHEN am.l10n_in_export_type IN ('deemed') THEN 'deemed_export'
                WHEN journal.l10n_in_import_export = true OR (partner.country_id IS NOT NULL AND partner.country_id != %s) THEN 'overseas'
                WHEN partner.vat IS NOT NULL AND partner.country_id = %s THEN 'regular'
                ELSE 'consumer'
            END
        FROM account_move AS am
        JOIN res_partner AS partner ON partner.id = am.partner_id
        JOIN res_partner AS delivery_partner ON delivery_partner.id = {delivery_partner_field}
        JOIN account_journal AS journal ON journal.id = am.journal_id
        JOIN res_company AS company ON company.id = journal.company_id
        JOIN res_partner AS company_unit_partner ON company_unit_partner.id = COALESCE(journal.l10n_in_gstin_partner_id, company.partner_id)
        JOIN company_with_l10n_in_coa AS in_company ON in_company.id = company.id

        WHERE am.id = account_move.id AND journal.type IN ('sale', 'purchase');"""

    cr.execute(account_move_update_query, (
        india_country_id, india_country_id, india_country_id,
        in_other_territory, india_country_id,india_country_id))

    res_partner_update_query = """WITH
        company_with_l10n_in_coa AS (
            SELECT c.id
            FROM res_company c
            JOIN ir_model_data d ON c.chart_template_id = d.res_id
                AND d.module = 'l10n_in'
                AND d.model = 'account.chart.template'
                AND d.name = 'indian_chart_template_standard'),

        sez_partner AS (SELECT commercial_partner_id
            FROM account_move
            JOIN company_with_l10n_in_coa in_company ON in_company.id = account_move.company_id
            WHERE account_move.l10n_in_export_type IN ('sez_with_igst','sez_without_igst')
                AND account_move.move_type != 'entry'
            GROUP BY commercial_partner_id),

        deemed_partner AS (SELECT commercial_partner_id
            FROM account_move
            JOIN company_with_l10n_in_coa in_company ON in_company.id = account_move.company_id
            WHERE account_move.l10n_in_export_type IN ('deemed')
                AND account_move.move_type != 'entry'
            GROUP BY commercial_partner_id)

        UPDATE res_partner u_p SET
            l10n_in_gst_treatment = CASE
                WHEN sez_p.commercial_partner_id IS NOT NULL THEN 'special_economic_zone'
                WHEN deemed_p.commercial_partner_id IS NOT NULL THEN 'deemed_export'
                WHEN u_p.country_id IS NOT NULL AND u_p.country_id != %s THEN 'overseas'
                WHEN u_p.vat IS NOT NULL AND u_p.country_id = %s THEN 'regular'
                ELSE 'consumer'
            END
            FROM res_partner p
            LEFT JOIN sez_partner sez_p ON sez_p.commercial_partner_id = p.commercial_partner_id
            LEFT JOIN deemed_partner deemed_p ON deemed_p.commercial_partner_id = p.commercial_partner_id
            WHERE p.id = u_p.id

        """
    cr.execute(res_partner_update_query, (india_country_id, india_country_id))

    #remove this fields in post because we use to update new fields.
    util.remove_field(cr, 'account.journal', 'l10n_in_import_export')
    util.remove_field(cr, 'account.move', 'l10n_in_export_type')
