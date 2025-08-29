from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "membership_membership_line"):
        return  # nosemgrep: no-early-return

    util.remove_view(cr, "partnership.membership_members_tree")
    util.remove_view(cr, "partnership.membership_product_search_form_view")
    util.remove_view(cr, "partnership.membership_products_form")
    util.remove_view(cr, "partnership.membership_products_kanban")
    util.remove_view(cr, "partnership.membership_products_tree")
    util.remove_view(cr, "partnership.report_membership_view_tree")
    util.remove_view(cr, "partnership.view_membership_invoice_view")
    util.remove_view(cr, "partnership.view_partner_form")
    util.remove_view(cr, "partnership.view_report_membership_graph1")
    util.remove_view(cr, "partnership.view_report_membership_pivot")
    util.remove_view(cr, "partnership.view_report_membership_search")
    util.remove_view(cr, "partnership.view_res_partner_member_filter")
    util.remove_record(cr, "partnership.action_membership_members_view_kanban")
    util.remove_record(cr, "partnership.action_membership_members_view_form")
    util.remove_record(cr, "partnership.action_membership_members_view_tree")
    util.remove_record(cr, "partnership.action_membership_product_view_kanban")
    util.remove_record(cr, "partnership.action_membership_product_view_form")
    util.remove_record(cr, "partnership.action_membership_product_view_tree")

    util.remove_record(cr, "partnership.menu_association")
    util.remove_record(cr, "partnership.menu_membership")
    util.remove_record(cr, "partnership.menu_marketing_config_association")
    util.remove_record(cr, "partnership.menu_membership_products")
    util.remove_record(cr, "partnership.ir_cron_update_membership")
    util.remove_record(cr, "partnership.action_report_membership_tree")
    util.remove_record(cr, "partnership.action_membership_members")
    util.remove_record(cr, "partnership.action_membership_products")
    util.remove_record(cr, "partnership.action_membership_invoice_view")

    member_state = {
        "none": "Non Member",
        "canceled": "Cancelled Member",
        "old": "Old Member",
        "waiting": "Waiting Member",
        "invoiced": "Invoiced Member",
        "free": "Free Member",
        "paid": "Paid Member",
    }

    query = util.format_query(
        cr,
        """
        WITH previous_membership_lines AS (
            SELECT ml.partner AS id,
                   CONCAT(
                          '<li>On ', ml.date, ' registered as member of ', {}, ' for ',
                          CASE
                              WHEN COALESCE(rc.position, rcc.position) = 'before' THEN COALESCE(rc.symbol, rcc.symbol) || ' ' || ml.member_price
                              ELSE ml.member_price || ' ' || COALESCE(rc.symbol, rcc.symbol)
                          END,
                          ', covering the period from ', ml.date_from,
                          ' to ', ml.date_to, ' (', %s::jsonb->>state, ')</li>'
                   ) AS line_string
              FROM membership_membership_line ml
              JOIN product_product pp
                ON pp.id = ml.membership_id
              JOIN product_template pt
                ON pt.id = pp.product_tmpl_id
         LEFT JOIN account_move_line aml
                ON aml.id = ml.account_invoice_line
         LEFT JOIN res_currency rc
                ON rc.id = aml.currency_id
         LEFT JOIN res_company c
                ON c.id = ml.company_id
         LEFT JOIN res_currency rcc
                ON rcc.id = c.currency_id
             WHERE pt.membership = true
        )
        INSERT INTO mail_message (res_id, model, author_id, message_type, date, body)
             SELECT r.id,
                    'res.partner',
                    %s,
                    'notification',
                    NOW() at time zone 'UTC',
                    CONCAT_WS(
                           E'\\n',
                           '<p>Membership history:</p>',
                           '<ul>',
                           ARRAY_TO_STRING(ARRAY_AGG(pml.line_string), E'\\n'),
                           '</ul>'
                    )
               FROM res_partner r
               JOIN previous_membership_lines pml
                 ON pml.id = r.id
           GROUP BY r.id
        """,
        util.pg_html_escape("pt.name->>'en_US'"),
    )
    cr.execute(query, [Json(member_state), util.ref(cr, "base.partner_root")])

    util.create_column(cr, "res_partner", "_upg_membership_product_id", "integer")
    # store assigned membership product id to each res partner to assign grades in post.
    cr.execute(
        """
            WITH last_ml_line AS (
                SELECT partner,
                       (ARRAY_AGG(id ORDER BY date_to DESC, date_from DESC, id DESC)
                        FILTER (WHERE state NOT IN ('none', 'canceled', 'old')))[1] AS max_id
                  FROM membership_membership_line
              GROUP BY partner
            )
            UPDATE res_partner
               SET _upg_membership_product_id = pt.id
              FROM last_ml_line lml
              JOIN membership_membership_line ml
                ON ml.id = lml.max_id
              JOIN product_product pp
                ON pp.id = ml.membership_id
              JOIN product_template pt
                ON pt.id = pp.product_tmpl_id
             WHERE res_partner.id = ml.partner
        """
    )

    util.remove_constraint(cr, "product_template", "product_template_membership_date_greater")
    util.remove_field(cr, "product.template", "membership_date_to")
    util.remove_field(cr, "product.template", "membership_date_from")
    util.remove_field(cr, "res.partner", "associate_member")
    util.remove_field(cr, "res.partner", "free_member")
    util.remove_field(cr, "res.partner", "member_lines")
    util.remove_field(cr, "res.partner", "membership_cancel")
    util.remove_field(cr, "res.partner", "membership_amount")
    # The data is used in post-migrate to update membership products and assign grades to res.partner
    util.remove_field(cr, "product.template", "membership", drop_column=False)
    util.remove_field(cr, "res.partner", "membership_start", drop_column=False)
    util.remove_field(cr, "res.partner", "membership_stop", drop_column=False)
    util.remove_field(cr, "res.partner", "membership_state", drop_column=False)

    util.remove_model(cr, "membership.invoice")
    util.remove_model(cr, "membership.membership_line")
    util.remove_model(cr, "report.membership")
