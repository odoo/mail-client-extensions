# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # XXX for pos_data_drinks, see script it pos_data_drinks module
    # TODO demo data for website_sale

    # This menu has been deduplicated into 2 modules. We have to choose one.
    menu = "menu_action_currency_form"
    if util.module_installed(cr, "account"):
        util.rename_xmlid(cr, "base." + menu, "account." + menu)
    elif util.module_installed(cr, "sales_team"):
        util.rename_xmlid(cr, "base." + menu, "sales_team." + menu)
    else:
        util.remove_menus(cr, [util.ref(cr, "base." + menu)])

    # no braces = from base module
    renames = """
        account.group_account_user
        association.menu_event_config
        base_setup.menu_config
        crm.menu_import_crm

        {sales_team,crm}.menu_crm_config_lead
        {sales_team,crm}.menu_crm_config_opportunity

        hr.group_hr_user
        hr.group_hr_manager
        hr.group_hr_attendance
        hr_expense.res_partner_address_fp

        {hr,hr_recruitment}.menu_hr_job_position
        {hr,hr_recruitment}.menu_hr_job_position_config

        mail.action_partner_mass_mail

        maintenance.group_equipment_manager
        membership.menu_association
        membership.menu_marketing_config_association

        {product,mrp}.product_assembly
        mrp.menu_mrp_config
        mrp.menu_mrp_root

        project.menu_main_pm
        project.menu_project_config_project
        project.menu_project_report
        project.menu_project_general_settings

        purchase.purchase_report
        purchase.menu_purchase_root

        {sales_team,sale}.menu_sales_config

        sale_stock.menu_aftersale
        sale_stock.menu_invoiced

        sales_team.menu_action_res_bank_form
        sales_team.menu_action_res_partner_bank_form
        sales_team.menu_sale_report
        sales_team.sales_team_config

        survey.group_survey_user
        survey.group_survey_manager

        {survey,survey_crm}.action_partner_survey_mail_crm

        website.group_website_publisher
        website.group_website_designer

        {website,sales_team}.salesteam_website_sales

        # not really part of xmlidpocalypse, but we can rename it here...
        {mass_mailing,website_mass_mailing}.group_website_popup_on_exit

        {project,website_project}.portal_project_rule
        {project,website_project}.portal_task_rule

        # enterprise
        {stock,stock_barcode}.demo_package
        {document,website_sign}.menu_document

    """

    for rename in util.splitlines(renames):
        try:
            src_id, dest_id = util.expand_braces(rename)
            dst_module = dest_id.partition(".")[0]
        except ValueError:
            dst_module, _, dst_name = rename.partition(".")
            src_id = "base." + dst_name
            dest_id = rename

        if util.module_installed(cr, dst_module):
            util.rename_xmlid(cr, src_id, dest_id)
        else:
            util.remove_record(cr, src_id)
