from odoo.upgrade import util


def migrate(cr, version):
    #################
    # DOCUMENTS.TAG #
    #################
    util.remove_record(cr, "documents.documents_finance_status_inbox")
    util.remove_record(cr, "documents.documents_finance_status_tc")
    util.remove_record(cr, "documents.documents_finance_status_validated")
    util.remove_record(cr, "documents.documents_finance_documents_Contracts")

    ############
    # CLEAN DB #
    ############
    # we might need those field for the sub-modules migration
    util.remove_column(cr, "documents_document", "_upg_old_folder_id")
    util.remove_field(cr, "documents.document", "create_share_id")
    util.remove_field(cr, "documents.document", "group_ids")
    util.remove_field(cr, "documents.document", "available_rule_ids")
    util.remove_field(cr, "documents.document", "is_shared")

    util.remove_field(cr, "documents.tag", "facet_id")
    util.remove_field(cr, "documents.tag", "folder_id")

    util.remove_model(cr, "documents.folder")
    util.remove_model(cr, "documents.facet")
    util.remove_model(cr, "documents.share")

    # TODO: migration action to server action / embedded actions
    util.remove_model(cr, "documents.workflow.rule")
    util.remove_model(cr, "documents.workflow.action")

    ###############
    # ACCESS.RULE #
    ###############
    util.remove_record(cr, "documents.documents_document_readonly_rule")
    util.remove_record(cr, "documents.documents_document_write_rule")
    util.remove_record(cr, "documents.documents_document_manager_rule")
    util.update_record_from_xml(cr, "documents.documents_document_global_rule")
    util.update_record_from_xml(cr, "documents.documents_document_global_write_rule")
    util.update_record_from_xml(cr, "documents.documents_access_global_rule_read")
    util.update_record_from_xml(cr, "documents.documents_access_global_rule_write")
    util.update_record_from_xml(cr, "documents.mail_plan_rule_group_document_manager_document")
    util.update_record_from_xml(cr, "documents.mail_plan_template_rule_group_document_manager_document")
    util.update_record_from_xml(cr, "documents.documents_tag_rule_portal")
