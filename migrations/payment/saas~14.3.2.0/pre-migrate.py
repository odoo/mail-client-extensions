from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # === PAYMENT ACQUIRER === #

    util.remove_field(cr, "payment.acquirer", "view_template_id")  # not stored
    util.remove_field(cr, "payment.acquirer", "registration_view_template_id")  # not stored
    util.remove_field(cr, "payment.acquirer", "check_validity")
    util.remove_field(cr, "payment.acquirer", "payment_flow")
    util.remove_field(cr, "payment.acquirer", "authorize_implemented")  # not stored
    util.remove_field(cr, "payment.acquirer", "fees_implemented")  # not stored
    util.remove_field(cr, "payment.acquirer", "token_implemented")  # not stored
    util.remove_field(cr, "payment.acquirer", "inbound_payment_method_ids")  # not stored

    if util.module_installed(cr, "payment_transfer"):
        util.move_field_to_module(cr, "payment.acquirer", "qr_code", "payment", "payment_transfer")
    else:
        util.remove_field(cr, "payment.acquirer", "qr_code")

    cr.execute(
        """
        UPDATE payment_acquirer
           SET provider = 'none'
         WHERE provider = 'manual'
        """
    )
    util.update_field_references(
        cr,
        "provider",
        "provider",
        only_models=("payment.acquirer",),
        domain_adapter=lambda op, right: (op, right.replace("manual", "none")),
    )

    util.create_column(cr, "payment_acquirer", "allow_tokenization", "bool")
    cr.execute(
        """
        UPDATE payment_acquirer
           SET allow_tokenization = TRUE
         WHERE save_token IN ('ask', 'always')
        """
    )
    util.remove_field(cr, "payment.acquirer", "save_token")

    util.create_column(cr, "payment_acquirer", "redirect_form_view_id", "int4")
    util.create_column(cr, "payment_acquirer", "inline_form_view_id", "int4")
    util.create_column(cr, "payment_acquirer", "support_authorization", "bool")
    util.create_column(cr, "payment_acquirer", "support_fees_computation", "bool")
    util.create_column(cr, "payment_acquirer", "support_tokenization", "bool")

    util.rename_xmlid(cr, *eb("payment.payment_acquirer_{ingenico,ogone}"))
    util.rename_xmlid(cr, *eb("payment.payment_acquirer_odoo{_by_adyen,}"))
    util.rename_xmlid(cr, *eb("payment.payment_acquirer_payu{,money}"))
    util.rename_xmlid(cr, *eb("payment{_test,}.payment_acquirer_test"))

    # === PAYMENT TRANSACTION === #

    util.remove_field(cr, "payment.transaction", "return_url")
    util.remove_field(cr, "payment.transaction", "html_3ds")

    util.rename_field(cr, "payment.transaction", "date", "last_state_change")
    util.rename_field(cr, "payment.transaction", "payment_token_id", "token_id")
    util.rename_field(cr, "payment.transaction", "is_processed", "is_post_processed")
    util.rename_field(cr, "payment.transaction", "invoice_ids_nbr", "invoices_count")

    util.create_column(cr, "payment_transaction", "operation", "varchar")
    util.create_column(cr, "payment_transaction", "tokenize", "bool")
    cr.execute(
        """
        UPDATE payment_transaction
           SET operation = CASE
               WHEN "type" IN ('form', 'form_save') THEN 'online_redirect'
               WHEN "type" = 'server2server' THEN 'online_token'
               WHEN "type" = 'validation' THEN 'validation'
           END
        """
    )
    util.remove_field(cr, "payment.transaction", "type")

    util.create_column(cr, "payment_transaction", "company_id", "int4")
    cr.execute(
        """
        UPDATE payment_transaction pt
           SET company_id = acq.company_id
          FROM payment_acquirer acq
         WHERE acq.id = pt.acquirer_id
         """
    )
    util.create_column(cr, "payment_transaction", "validation_route", "varchar")
    util.create_column(cr, "payment_transaction", "landing_route", "varchar")
    util.create_column(cr, "payment_transaction", "partner_state_id", "int4")
    cr.execute(
        """
        UPDATE payment_transaction pt
           SET partner_state_id = p.state_id
          FROM res_partner p
         WHERE p.id = pt.partner_id
         """
    )
    util.create_column(cr, "payment_transaction", "callback_is_done", "bool")

    # === PAYMENT TOKEN === #

    util.remove_field(cr, "payment.token", "short_name")

    util.move_field_to_module(cr, "payment.token", "provider", "payment_authorize", "payment")  # not stored

    util.rename_field(cr, "payment.token", "payment_ids", "transaction_ids")

    cr.execute(
        """
        UPDATE payment_token
           SET name = 'MIG_' || id
         WHERE name IS NULL
        """
    )

    # === IR RULE === #

    util.rename_xmlid(cr, *eb("payment.payment_token_{salesman,billing}_rule"))

    # === IR UI VIEW === #

    util.remove_view(cr, "payment.default_acquirer_button")

    util.rename_xmlid(cr, *eb("payment.{,payment_}acquirer_form"))
    util.rename_xmlid(cr, *eb("payment.{,payment_}acquirer_kanban"))
    util.rename_xmlid(cr, *eb("payment.{,payment_}acquirer_list"))
    util.rename_xmlid(cr, *eb("payment.{,payment_}acquirer_search"))
    util.rename_xmlid(cr, *eb("payment.{,payment_}transaction_form"))
    util.rename_xmlid(cr, *eb("payment.{,payment_}transaction_list"))
    util.rename_xmlid(cr, "payment.transaction_view_kanban", "payment.payment_transaction_kanban")
    util.rename_xmlid(cr, "payment.transaction", "payment.payment_transaction_search")
    util.rename_xmlid(cr, "payment.payment_token_tree_view", "payment.payment_token_list")
    util.rename_xmlid(cr, "payment.payment_token_view_search", "payment.payment_token_search")
    util.rename_xmlid(cr, "payment.action_payment_tx_ids", "payment.action_payment_transaction_linked_to_token")
    util.rename_xmlid(cr, *eb("payment.payment_token_form{_view,}"))
    util.rename_xmlid(cr, "payment.payment_token_action", "payment.action_payment_token")
    util.rename_xmlid(cr, *eb("payment.payment_icon_form{_view,}"))

    util.rename_xmlid(cr, "payment.pay_methods", "payment.payment_methods")
    util.rename_xmlid(cr, "payment.payment_confirmation_status", "payment.transaction_status")
    util.rename_xmlid(cr, "payment.payment_tokens_list", "payment.checkout")
    util.rename_xmlid(cr, "payment.payment_process_page", "payment.payment_status")
