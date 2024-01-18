# -*- coding: utf-8 -*-
import logging

from odoo import api, models, release

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base."
_logger = logging.getLogger(NS + __name__)


def _odoo_com(cr):
    queries = [
        [
            "upgrade_fk_ir_model_idx_1",
            "CREATE INDEX upgrade_fk_ir_model_idx_1 ON public.account_report USING btree (custom_handler_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_10",
            "CREATE INDEX upgrade_fk_ir_model_idx_10 ON public.documents_link_to_record_wizard USING btree (model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_4",
            "CREATE INDEX upgrade_fk_ir_model_idx_4 ON public.base_automation USING btree (trg_date_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_5",
            "CREATE INDEX upgrade_fk_ir_model_idx_5 ON public.base_automation USING btree (trg_date_resource_field_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_14",
            "CREATE INDEX upgrade_fk_ir_model_idx_14 ON public.gamification_goal_definition USING btree (batch_distinctive_field)",
        ],
        # ['upgrade_fk_ir_model_idx_21', 'CREATE INDEX upgrade_fk_ir_model_idx_21 ON public.hr_contract_salary_benefit USING btree (manual_res_field_id)'],
        [
            "upgrade_fk_ir_model_idx_27",
            "CREATE INDEX upgrade_fk_ir_model_idx_27 ON public.ir_act_server USING btree (crud_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_11",
            "CREATE INDEX upgrade_fk_ir_model_idx_11 ON public.documents_workflow_rule USING btree (link_model)",
        ],
        [
            "upgrade_fk_ir_model_idx_16",
            "CREATE INDEX upgrade_fk_ir_model_idx_16 ON public.gamification_goal_definition USING btree (field_id)",
        ],
        # ['upgrade_fk_ir_model_idx_19', 'CREATE INDEX upgrade_fk_ir_model_idx_19 ON public.hr_contract_salary_benefit USING btree (fold_res_field_id)'],
        [
            "upgrade_fk_ir_model_idx_25",
            "CREATE INDEX upgrade_fk_ir_model_idx_25 ON public.ir_act_report_xml USING btree (binding_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_7",
            "CREATE INDEX upgrade_fk_ir_model_idx_7 ON public.crm_case_log USING btree (model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_17",
            "CREATE INDEX upgrade_fk_ir_model_idx_17 ON public.gamification_goal_definition USING btree (model_id)",
        ],
        # ['upgrade_fk_ir_model_idx_22', 'CREATE INDEX upgrade_fk_ir_model_idx_22 ON public.hr_contract_salary_benefit USING btree (res_field_id)'],
        [
            "upgrade_fk_ir_model_idx_26",
            "CREATE INDEX upgrade_fk_ir_model_idx_26 ON public.ir_act_server USING btree (binding_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_15",
            "CREATE INDEX upgrade_fk_ir_model_idx_15 ON public.gamification_goal_definition USING btree (field_date_id)",
        ],
        # ['upgrade_fk_ir_model_idx_18', 'CREATE INDEX upgrade_fk_ir_model_idx_18 ON public.hr_contract_salary_benefit USING btree (cost_res_field_id)'],
        [
            "upgrade_fk_ir_model_idx_23",
            "CREATE INDEX upgrade_fk_ir_model_idx_23 ON public.hr_contract_salary_personal_info USING btree (res_field_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_28",
            "CREATE INDEX upgrade_fk_ir_model_idx_28 ON public.ir_act_server USING btree (link_field_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_24",
            "CREATE INDEX upgrade_fk_ir_model_idx_24 ON public.ir_act_client USING btree (binding_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_29",
            "CREATE INDEX upgrade_fk_ir_model_idx_29 ON public.ir_act_url USING btree (binding_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_30",
            "CREATE INDEX upgrade_fk_ir_model_idx_30 ON public.ir_act_window USING btree (binding_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_33",
            "CREATE INDEX upgrade_fk_ir_model_idx_33 ON public.ir_model_fields USING btree (related_field_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_34",
            "CREATE INDEX upgrade_fk_ir_model_idx_34 ON public.ir_model_fields USING btree (relation_field_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_57",
            "CREATE INDEX upgrade_fk_ir_model_idx_57 ON public.privacy_lookup_wizard_line USING btree (res_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_35",
            "CREATE INDEX upgrade_fk_ir_model_idx_35 ON public.ir_model USING btree (website_form_default_field_id)",
        ],
        [
            "upgrade_fk_related_idx_5",
            "CREATE INDEX upgrade_fk_related_idx_5 ON public.account_move_line USING btree (account_id)",
        ],
        [
            "upgrade_fk_related_idx_80",
            "CREATE INDEX upgrade_fk_related_idx_80 ON public.account_edi_document USING btree (attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_94",
            "CREATE INDEX upgrade_fk_related_idx_94 ON public.account_partial_reconcile USING btree (credit_move_id)",
        ],
        [
            "upgrade_fk_related_idx_100",
            "CREATE INDEX upgrade_fk_related_idx_100 ON public.appointment_answer_input USING btree (calendar_event_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_51",
            "CREATE INDEX upgrade_fk_ir_model_idx_51 ON public.mailing_filter USING btree (mailing_model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_52",
            "CREATE INDEX upgrade_fk_ir_model_idx_52 ON public.mailing_mailing USING btree (mailing_model_id)",
        ],
        [
            "upgrade_fk_related_idx_2",
            "CREATE INDEX upgrade_fk_related_idx_2 ON public.hr_resume_line USING btree (employee_id)",
        ],
        [
            "upgrade_fk_related_idx_17",
            "CREATE INDEX upgrade_fk_related_idx_17 ON public.account_move_line USING btree (purchase_line_id) WHERE (purchase_line_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_53",
            "CREATE INDEX upgrade_fk_related_idx_53 ON public.account_analytic_line USING btree (move_line_id)",
        ],
        [
            "upgrade_fk_related_idx_111",
            "CREATE INDEX upgrade_fk_related_idx_111 ON public.bus_presence USING btree (user_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_53",
            "CREATE INDEX upgrade_fk_ir_model_idx_53 ON public.marketing_campaign USING btree (unique_field_id)",
        ],
        [
            "upgrade_fk_related_idx_142",
            "CREATE INDEX upgrade_fk_related_idx_142 ON public.discuss_channel_member USING btree (channel_id)",
        ],
        [
            "upgrade_fk_related_idx_151",
            "CREATE INDEX upgrade_fk_related_idx_151 ON public.event_registration USING btree (sale_order_line_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_59",
            "CREATE INDEX upgrade_fk_ir_model_idx_59 ON public.process_node USING btree (model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_61",
            "CREATE INDEX upgrade_fk_ir_model_idx_61 ON public.sms_template USING btree (model_id)",
        ],
        [
            "upgrade_fk_ir_model_idx_63",
            "CREATE INDEX upgrade_fk_ir_model_idx_63 ON public.whatsapp_template USING btree (model_id)",
        ],
        [
            "upgrade_fk_related_idx_15",
            "CREATE INDEX upgrade_fk_related_idx_15 ON public.account_move_line USING btree (product_id)",
        ],
        [
            "upgrade_fk_related_idx_96",
            "CREATE INDEX upgrade_fk_related_idx_96 ON public.account_partial_reconcile USING btree (debit_move_id)",
        ],
        [
            "upgrade_fk_related_idx_199",
            "CREATE INDEX upgrade_fk_related_idx_199 ON public.gamification_goal USING btree (line_id)",
        ],
        [
            "upgrade_fk_related_idx_218",
            "CREATE INDEX upgrade_fk_related_idx_218 ON public.hr_applicant USING btree (message_main_attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_220",
            "CREATE INDEX upgrade_fk_related_idx_220 ON public.hr_applicant USING btree (partner_id)",
        ],
        [
            "upgrade_fk_related_idx_41",
            "CREATE INDEX upgrade_fk_related_idx_41 ON public.account_analytic_line USING btree (account_id)",
        ],
        [
            "upgrade_fk_related_idx_107",
            "CREATE INDEX upgrade_fk_related_idx_107 ON public.calendar_attendee USING btree (event_id)",
        ],
        [
            "upgrade_fk_related_idx_16",
            "CREATE INDEX upgrade_fk_related_idx_16 ON public.account_move_line USING btree (product_uom_id)",
        ],
        [
            "upgrade_fk_related_idx_207",
            "CREATE INDEX upgrade_fk_related_idx_207 ON public.hr_analytic_timesheet USING btree (line_id)",
        ],
        [
            "upgrade_fk_related_idx_228",
            "CREATE INDEX upgrade_fk_related_idx_228 ON public.hr_attendance USING btree (employee_id)",
        ],
        [
            "upgrade_fk_related_idx_234",
            "CREATE INDEX upgrade_fk_related_idx_234 ON public.hr_expense USING btree (product_id)",
        ],
        [
            "upgrade_fk_related_idx_86",
            "CREATE INDEX upgrade_fk_related_idx_86 ON public.discuss_channel USING btree (group_public_id) WHERE (group_public_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_108",
            "CREATE INDEX upgrade_fk_related_idx_108 ON public.calendar_attendee USING btree (partner_id)",
        ],
        [
            "upgrade_fk_related_idx_233",
            "CREATE INDEX upgrade_fk_related_idx_233 ON public.hr_expense USING btree (message_main_attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_241",
            "CREATE INDEX upgrade_fk_related_idx_241 ON public.hr_leave USING btree (employee_id)",
        ],
        [
            "upgrade_fk_related_idx_247",
            "CREATE INDEX upgrade_fk_related_idx_247 ON public.hr_leave USING btree (message_main_attachment_id) WHERE (message_main_attachment_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_127",
            "CREATE INDEX upgrade_fk_related_idx_127 ON public.crm_lead USING btree (partner_id)",
        ],
        [
            "upgrade_fk_related_idx_239",
            "CREATE INDEX upgrade_fk_related_idx_239 ON public.hr_leave USING btree (department_id)",
        ],
        [
            "upgrade_fk_related_idx_244",
            "CREATE INDEX upgrade_fk_related_idx_244 ON public.hr_leave USING btree (holiday_status_id)",
        ],
        [
            "upgrade_fk_related_idx_248",
            "CREATE INDEX upgrade_fk_related_idx_248 ON public.hr_leave USING btree (mode_company_id) WHERE (mode_company_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_252",
            "CREATE INDEX upgrade_fk_related_idx_252 ON public.hr_leave USING btree (user_id)",
        ],
        [
            "upgrade_fk_related_idx_174",
            "CREATE INDEX upgrade_fk_related_idx_174 ON public.sale_order_line USING btree (product_id)",
        ],
        [
            "upgrade_fk_related_idx_269",
            "CREATE INDEX upgrade_fk_related_idx_269 ON public.hr_payslip USING btree (message_main_attachment_id) WHERE (message_main_attachment_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_300",
            "CREATE INDEX upgrade_fk_related_idx_300 ON public.res_partner USING btree (l10n_mx_edi_addenda) WHERE (l10n_mx_edi_addenda IS NOT NULL)",
        ],
        # ['upgrade_fk_related_idx_307', 'CREATE INDEX upgrade_fk_related_idx_307 ON public.mail_tracking_value USING btree (field_id)'],
        [
            "upgrade_fk_related_idx_278",
            "CREATE INDEX upgrade_fk_related_idx_278 ON public.hr_payslip_line USING btree (salary_rule_id)",
        ],
        [
            "upgrade_fk_related_idx_316",
            "CREATE INDEX upgrade_fk_related_idx_316 ON public.hr_work_entry USING btree (contract_id)",
        ],
        [
            "upgrade_fk_related_idx_392",
            "CREATE INDEX upgrade_fk_related_idx_392 ON public.marketing_participant USING btree (model_id)",
        ],
        [
            "upgrade_fk_related_idx_301",
            "CREATE INDEX upgrade_fk_related_idx_301 ON public.res_partner USING btree (parent_id) WHERE (parent_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_350",
            "CREATE INDEX upgrade_fk_related_idx_350 ON public.mail_activity USING btree (activity_type_id)",
        ],
        [
            "upgrade_fk_related_idx_356",
            "CREATE INDEX upgrade_fk_related_idx_356 ON public.mail_activity USING btree (user_id)",
        ],
        [
            "upgrade_fk_related_idx_359",
            "CREATE INDEX upgrade_fk_related_idx_359 ON public.mail_alias USING btree (alias_parent_model_id)",
        ],
        [
            "upgrade_fk_related_idx_365",
            "CREATE INDEX upgrade_fk_related_idx_365 ON public.mail_link_preview USING btree (message_id)",
        ],
        [
            "upgrade_fk_related_idx_369",
            "CREATE INDEX upgrade_fk_related_idx_369 ON public.mail_message_reaction USING btree (message_id)",
        ],
        [
            "upgrade_fk_related_idx_293",
            "CREATE INDEX upgrade_fk_related_idx_293 ON public.res_partner USING btree (commercial_partner_id)",
        ],
        [
            "upgrade_fk_related_idx_298",
            "CREATE INDEX upgrade_fk_related_idx_298 ON public.res_partner USING btree (grade_id) WHERE (grade_id IS NOT NULL)",
        ],
        # ['upgrade_fk_related_idx_308', 'CREATE INDEX upgrade_fk_related_idx_308 ON public.mail_tracking_value USING btree (mail_message_id)'],
        [
            "upgrade_fk_related_idx_420",
            "CREATE INDEX upgrade_fk_related_idx_420 ON public.project_task_user_rel USING btree (stage_id)",
        ],
        [
            "upgrade_fk_related_idx_422",
            "CREATE INDEX upgrade_fk_related_idx_422 ON public.project_task_type USING btree (mail_template_id) WHERE (mail_template_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_423",
            "CREATE INDEX upgrade_fk_related_idx_423 ON public.project_task_type USING btree (rating_template_id) WHERE (rating_template_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_436",
            "CREATE INDEX upgrade_fk_related_idx_436 ON public.purchase_order USING btree (picking_type_id)",
        ],
        [
            "upgrade_fk_related_idx_322",
            "CREATE INDEX upgrade_fk_related_idx_322 ON public.ir_attachment USING btree (original_id) WHERE (original_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_327",
            "CREATE INDEX upgrade_fk_related_idx_327 ON public.ir_property USING btree (company_id)",
        ],
        [
            "upgrade_fk_related_idx_328",
            "CREATE INDEX upgrade_fk_related_idx_328 ON public.ir_property USING btree (fields_id)",
        ],
        [
            "upgrade_fk_related_idx_336",
            "CREATE INDEX upgrade_fk_related_idx_336 ON public.calendar_event USING btree (res_model_id)",
        ],
        [
            "upgrade_fk_related_idx_355",
            "CREATE INDEX upgrade_fk_related_idx_355 ON public.mail_activity USING btree (res_model_id)",
        ],
        [
            "upgrade_fk_related_idx_358",
            "CREATE INDEX upgrade_fk_related_idx_358 ON public.mail_alias USING btree (alias_model_id)",
        ],
        [
            "upgrade_fk_related_idx_377",
            "CREATE INDEX upgrade_fk_related_idx_377 ON public.mail_template USING btree (model_id)",
        ],
        [
            "upgrade_fk_related_idx_378",
            "CREATE INDEX upgrade_fk_related_idx_378 ON public.mail_template USING btree (ref_ir_act_window) WHERE (ref_ir_act_window IS NOT NULL)",
        ],
        # ['upgrade_fk_related_idx_383', 'CREATE INDEX upgrade_fk_related_idx_383 ON public.mailing_subscription USING btree (contact_id)'],
        [
            "upgrade_fk_related_idx_448",
            "CREATE INDEX upgrade_fk_related_idx_448 ON public.purchase_order_line USING btree (product_id)",
        ],
        [
            "upgrade_fk_related_idx_455",
            "CREATE INDEX upgrade_fk_related_idx_455 ON public.rating_rating USING btree (parent_res_model_id)",
        ],
        [
            "upgrade_fk_related_idx_470",
            "CREATE INDEX upgrade_fk_related_idx_470 ON public.res_users USING btree (last_seen_phone_call) WHERE (last_seen_phone_call IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_472",
            "CREATE INDEX upgrade_fk_related_idx_472 ON public.res_users USING btree (partner_id)",
        ],
        [
            "upgrade_fk_related_idx_698",
            "CREATE INDEX upgrade_fk_related_idx_698 ON public.l10n_mx_edi_document USING btree (attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_720",
            "CREATE INDEX upgrade_fk_related_idx_720 ON public.payment_transaction USING btree (callback_model_id)",
        ],
        [
            "upgrade_fk_related_idx_445",
            "CREATE INDEX upgrade_fk_related_idx_445 ON public.purchase_order_line USING btree (order_id)",
        ],
        [
            "upgrade_fk_related_idx_454",
            "CREATE INDEX upgrade_fk_related_idx_454 ON public.rating_rating USING btree (message_id) WHERE (message_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_459",
            "CREATE INDEX upgrade_fk_related_idx_459 ON public.rating_rating USING btree (res_model_id)",
        ],
        [
            "upgrade_fk_related_idx_477",
            "CREATE INDEX upgrade_fk_related_idx_477 ON public.resource_calendar_leaves USING btree (calendar_id)",
        ],
        [
            "upgrade_fk_related_idx_480",
            "CREATE INDEX upgrade_fk_related_idx_480 ON public.resource_calendar_leaves USING btree (resource_id)",
        ],
        [
            "upgrade_fk_related_idx_483",
            "CREATE INDEX upgrade_fk_related_idx_483 ON public.sale_order_option USING btree (order_id)",
        ],
        [
            "upgrade_fk_related_idx_496",
            "CREATE INDEX upgrade_fk_related_idx_496 ON public.sale_subscription USING btree (message_main_attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_537",
            "CREATE INDEX upgrade_fk_related_idx_537 ON public.slide_slide_partner USING btree (slide_id)",
        ],
        [
            "upgrade_fk_related_idx_530",
            "CREATE INDEX upgrade_fk_related_idx_530 ON public.sign_request_item USING btree (partner_id)",
        ],
        [
            "upgrade_fk_related_idx_558",
            "CREATE INDEX upgrade_fk_related_idx_558 ON public.website_track USING btree (page_id)",
        ],
        [
            "upgrade_fk_related_idx_635",
            "CREATE INDEX upgrade_fk_related_idx_635 ON public.account_move USING btree (message_main_attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_639",
            "CREATE INDEX upgrade_fk_related_idx_639 ON public.account_move USING btree (payment_id)",
        ],
        # ['upgrade_fk_related_idx_557', 'CREATE INDEX upgrade_fk_related_idx_557 ON public.voip_call USING btree (user_id)'],
        [
            "upgrade_fk_related_idx_570",
            "CREATE INDEX upgrade_fk_related_idx_570 ON public.documents_document USING btree (attachment_id)",
        ],
        [
            "upgrade_fk_related_idx_584",
            "CREATE INDEX upgrade_fk_related_idx_584 ON public.project_task USING btree (displayed_image_id) WHERE (displayed_image_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_594",
            "CREATE INDEX upgrade_fk_related_idx_594 ON public.project_task USING btree (stage_id)",
        ],
        [
            "upgrade_fk_related_idx_618",
            "CREATE INDEX upgrade_fk_related_idx_618 ON public.account_move USING btree (commercial_partner_id)",
        ],
        [
            "upgrade_fk_related_idx_629",
            "CREATE INDEX upgrade_fk_related_idx_629 ON public.account_move USING btree (l10n_id_attachment_id) WHERE (l10n_id_attachment_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_632",
            "CREATE INDEX upgrade_fk_related_idx_632 ON public.account_move USING btree (l10n_mx_edi_cfdi_attachment_id) WHERE (l10n_mx_edi_cfdi_attachment_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_678",
            "CREATE INDEX upgrade_fk_related_idx_678 ON public.sale_order USING btree (partner_id)",
        ],
        [
            "upgrade_fk_related_idx_601",
            "CREATE INDEX upgrade_fk_related_idx_601 ON public.product_template USING btree (email_template_id) WHERE (email_template_id IS NOT NULL)",
        ],
        [
            "upgrade_fk_related_idx_609",
            "CREATE INDEX upgrade_fk_related_idx_609 ON public.product_template USING btree (uom_id)",
        ],
        [
            "upgrade_fk_related_idx_689",
            "CREATE INDEX upgrade_fk_related_idx_689 ON public.sale_order USING btree (sale_order_template_id)",
        ],
        [
            "upgrade_fk_related_idx_696",
            "CREATE INDEX upgrade_fk_related_idx_696 ON public.sale_order USING btree (warehouse_id)",
        ],
        [
            "upgrade_fk_related_idx_706",
            "CREATE INDEX upgrade_fk_related_idx_706 ON public.account_payment USING btree (message_main_attachment_id) WHERE (message_main_attachment_id IS NOT NULL)",
        ],
        # ['upgrade_fk_related_idx_001', 'create index upgrade_fk_related_idx_001 ON res_users(last_seen_phone_call) where last_seen_phone_call IS NOT NULL'],
        # ['upgrade_fk_related_idx_002', 'create index upgrade_fk_related_idx_002 ON voip_phonecall_log_wizard(phonecall_id) where phonecall_id IS NOT NULL'],
        # ['upgrade_fk_related_idx_003', 'create index upgrade_fk_related_idx_003 on mail_activity(voip_phonecall_id) where voip_phonecall_id IS NOT NULL'],
        [
            "upgrade_fk_related_idx_004",
            "create index upgrade_fk_related_idx_004 on ir_attachment(res_model, res_field, id)",
        ],
        [
            "upgrade_fk_related_idx_005",
            "create index upgrade_fk_related_idx_005 on mail_tracking_value(id) where field_type = 'monetary'",
        ],
    ]
    fk_names, create_index_queries = zip(*queries)
    util.ENVIRON["__created_fk_idx"] = list(fk_names)
    _logger.info("creating %s indexes (might be slow)", len(create_index_queries))
    util.parallel_execute(cr, create_index_queries)
    return True


def migrate(cr, version):
    if util.dbuuid(cr) == "8851207e-1ff9-11e0-a147-001cc0f2115e":
        return _odoo_com(cr)

    cr.execute("ANALYZE")  # update statistics
    create_index_queries = []
    util.ENVIRON["__created_fk_idx"] = []

    create_index_queries.append(
        "CREATE INDEX upg_attachment_cleanup_speedup_idx ON ir_attachment(res_model, res_field, id)"
    )
    util.ENVIRON["__created_fk_idx"].append("upg_attachment_cleanup_speedup_idx")

    if release.version_info[:2] == (16, 0) and util.column_exists(cr, "mail_message", "email_layout_xmlid"):
        create_index_queries.append("CREATE INDEX upg_mailmsg_layout_xid ON mail_message(email_layout_xmlid)")
        util.ENVIRON["__created_fk_idx"].append("upg_mailmsg_layout_xid")

    if util.column_exists(cr, "website_visitor", "push_token"):
        create_index_queries.append(
            "create index tmp_mig_websitevisitortoken_speedup_idx on website_visitor(id) WHERE push_token IS NOT NULL"
        )
        util.ENVIRON["__created_fk_idx"].append("tmp_mig_websitevisitortoken_speedup_idx")

    # create indexes on `ir_model{,_fields}` to speed up models/fields deletion
    cr.execute(
        """
           SELECT quote_ident(concat('upgrade_fk_ir_model_idx_',
                                     ROW_NUMBER() OVER(ORDER BY con.conname)::varchar
                  )) AS index_name,
                  quote_ident(cl1.relname) as table,
                  quote_ident(att1.attname) as column
             FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                  pg_attribute as att1, pg_attribute as att2
            WHERE con.conrelid = cl1.oid
              AND con.confrelid = cl2.oid
              AND array_lower(con.conkey, 1) = 1
              AND con.conkey[1] = att1.attnum
              AND att1.attrelid = cl1.oid
              AND cl2.relname IN ('ir_model', 'ir_model_fields')
              AND att2.attname = 'id'
              AND array_lower(con.confkey, 1) = 1
              AND con.confkey[1] = att2.attnum
              AND att2.attrelid = cl2.oid
              AND con.contype = 'f'
              AND NOT EXISTS (
                    -- FIND EXISTING INDEXES
                  SELECT 1
                    FROM (select *, unnest(indkey) as unnest_indkey from pg_index) x
                    JOIN pg_class c ON c.oid = x.indrelid
                    JOIN pg_class i ON i.oid = x.indexrelid
                    JOIN pg_attribute a ON (a.attrelid=c.oid AND a.attnum=x.unnest_indkey)
                   WHERE (c.relkind = ANY (ARRAY['r'::"char", 'm'::"char"]))
                     AND i.relkind = 'i'::"char"
                     AND c.relname = cl1.relname
                GROUP BY i.relname, x.indisunique, x.indisprimary
                 HAVING array_agg(a.attname::text) = ARRAY[att1.attname::text]
              )
        """
    )
    for index_name, table_name, column_name in cr.fetchall():
        util.ENVIRON["__created_fk_idx"].append(index_name)
        create_index_queries.append("CREATE INDEX %s ON %s(%s)" % (index_name, table_name, column_name))

    # Return all FK columns from BIG tables
    cr.execute(
        """
        SELECT quote_ident(cl1.relname) AS big_table,
               quote_ident(att1.attname) AS big_table_column,
               s.null_frac > 0.9 -- less than 10 percent is not null
          FROM pg_constraint AS con
          JOIN pg_class AS cl1
            ON con.conrelid = cl1.oid
          JOIN pg_namespace AS pg_n
            ON pg_n.oid = cl1.relnamespace
          JOIN pg_class AS cl2
            ON con.confrelid = cl2.oid
          JOIN pg_attribute AS att1
            ON att1.attrelid = cl1.oid
          JOIN pg_attribute AS att2
            ON att2.attrelid = cl2.oid
     LEFT JOIN pg_stats AS s
            ON s.tablename = cl1.relname
           AND s.attname = att1.attname
           AND s.schemaname = current_schema
     LEFT JOIN pg_index x
            ON x.indrelid = cl1.oid
            -- att1 is one of the KEY columns, not just a included one, included columns won't speed up searches
           AND att1.attnum = ANY (x.indkey[1:x.{}])
         WHERE cl1.reltuples >= %s -- arbitrary number saying this is a big table
           AND cl1.relkind = 'r' -- only select the tables
           AND att1.attname NOT IN ('create_uid', 'write_uid')
           AND x.indrelid IS NULL -- there is no index with the included column
           AND pg_n.nspname = current_schema
            -- the rest is to ensure this is a FK
           AND array_lower(con.conkey, 1) = 1
           AND con.conkey[1] = att1.attnum
           AND att2.attname = 'id'
           AND array_lower(con.confkey, 1) = 1
           AND con.confkey[1] = att2.attnum
           AND con.contype = 'f'
        """.format(
            "indnkeyatts" if cr._cnx.server_version >= 110000 else "indnatts"
        ),
        [util.BIG_TABLE_THRESHOLD],
    )
    for i, (big_table, big_table_column, partial) in enumerate(cr.fetchall(), start=1):
        index_name = "upgrade_fk_related_idx_{}".format(i)
        util.ENVIRON["__created_fk_idx"].append(index_name)
        query = "CREATE INDEX {index_name} ON {big_table}({big_table_column})"
        if partial:
            query += " WHERE {big_table_column} IS NOT NULL"
        create_index_queries.append(
            query.format(index_name=index_name, big_table=big_table, big_table_column=big_table_column)
        )

    if create_index_queries:
        _logger.info("creating %s indexes (might be slow)", len(create_index_queries))
        util.parallel_execute(cr, create_index_queries)


class Model(models.Model):
    _inherit = "ir.model"
    _module = "base"

    @api.model
    def _register_hook(self):
        super(Model, self)._register_hook()
        index_names = util.ENVIRON.get("__created_fk_idx", [])
        if index_names:
            drop_index_queries = []
            for index_name in index_names:
                drop_index_queries.append('DROP INDEX IF EXISTS "%s"' % (index_name,))
            _logger.info("dropping %s indexes", len(drop_index_queries))
            util.parallel_execute(self.env.cr, drop_index_queries)
