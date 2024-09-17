from odoo.upgrade import util


def migrate(cr, version):
    # Define adapter for updating the 'state' field usage.
    def _adapter(leaf, _or, _neg):
        _, op, value = leaf
        new_op = "=" if (op == "=" and value) or (op == "!=" and not value) else "!="
        return [("state", new_op, "canceled")]

    # Set 'canceled' state on sign requests if any of its sign request items were previously ignored.
    sign_request_update_query = """
        WITH to_cancel AS (
           SELECT r.id
             FROM sign_request_item i
             JOIN sign_request r
               ON r.id = i.sign_request_id
            WHERE i.ignored is true
              AND i.state != 'completed'
              AND r.state IN ('sent', 'shared')
              AND {parallel_filter}
         GROUP BY r.id
        )
        UPDATE sign_request r
           SET state = 'canceled'
          FROM to_cancel t
         WHERE t.id = r.id
    """
    util.explode_execute(cr, sign_request_update_query, table="sign_request", alias="r")

    # Do the same for sign_request_items: set state as 'canceled' when it was previously ignored.
    sign_request_item_update_query = """
        UPDATE sign_request_item
           SET state = 'canceled'
         WHERE ignored = true
           AND state != 'completed'
    """
    util.explode_execute(cr, sign_request_item_update_query, table="sign_request_item")

    # Update the selection values from 'refused' to 'canceled' and remove old field and view.
    util.change_field_selection_values(cr, "sign.request", "state", {"refused": "canceled"})
    util.change_field_selection_values(cr, "sign.request.item", "state", {"refused": "canceled"})
    util.update_field_usage(cr, "sign.request.item", "ignored", "state", domain_adapter=_adapter)
    util.remove_field(cr, "sign.request.item", "ignored")
    util.rename_xmlid(cr, "sign.ignore_sign_request_item", "sign.canceled_sign_request_item", noupdate=False)

    util.remove_record(cr, "sign.sign_request_my_requests_action")
    util.remove_record(cr, "sign.sign_request_waiting_for_me_action")
    util.remove_record(cr, "sign.sign_request_waiting_for_me")
    util.rename_xmlid(cr, "sign.sign_request_my_requests", "sign.sign_request_my_documents")
