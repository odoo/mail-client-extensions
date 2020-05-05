# -*- coding: utf-8 -*-
import logging
import datetime

from odoo.addons.base.maintenance.migrations import util
from odoo.tools import float_round
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

NS = "odoo.addons.base.maintenance.migrations.account.saas~12.3."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    if util.version_gte("saas~12.4"):
        sql_dict = {
            "invoice_table": "account_move",
            "invoice_id_field": "move_id",
            "where_criteria": "move_id = move.id AND move.type NOT IN ('in_refund', 'in_invoice', 'out_refund', 'out_invoice')",
        }
    else:
        sql_dict = {
            "invoice_table": "account_invoice",
            "invoice_id_field": "invoice_id",
            "where_criteria": "invoice_id IS NULL",
        }

    if not util.table_exists(cr, "tax_accounts_v12_bckp"):
        return True
    env = util.env(cr)
    # Abracadabra !
    # We consider the module was only updated. So, now, some tax_line_id are set while there is not tax_repartition_line_id
    # on the move lines. tax_line_id is supposed to be related on tax_repartition_line_id, so we have to fix this
    # inconsistency first
    for tax in env["account.tax"].with_context(active_test=False).search([]):
        if not tax.invoice_repartition_line_ids and not tax.refund_repartition_line_ids:
            tax.write(
                tax.with_context(default_company_id=tax.company_id).default_get(
                    ["invoice_repartition_line_ids", "refund_repartition_line_ids", "company_id"]
                )
            )
        else:
            raise UserError("Tax %s has already some repartition lines. It should not at this point." % tax.id)

    cr.execute(
        """
        UPDATE account_move_line
           SET tax_repartition_line_id = tx_rep.id
          FROM account_tax_repartition_line tx_rep, %(invoice_table)s move
         WHERE %(where_criteria)s
           AND tax_line_id = tx_rep.invoice_tax_id
           AND tx_rep.repartition_type = 'tax'
    """
        % sql_dict
    )
    cr.execute(
        """
        UPDATE account_move_line
           SET tax_repartition_line_id = tx_rep.id
          FROM account_tax_repartition_line tx_rep, %(invoice_table)s move
         WHERE %(invoice_id_field)s = move.id
           AND move.type IN ('in_refund', 'out_refund')
           AND tax_line_id = tx_rep.refund_tax_id
           AND tx_rep.repartition_type = 'tax'
    """
        % sql_dict
    )
    cr.execute(
        """
        UPDATE account_move_line
           SET tax_repartition_line_id = tx_rep.id
          FROM account_tax_repartition_line tx_rep, %(invoice_table)s move
         WHERE %(invoice_id_field)s = move.id
           AND move.type IN ('in_invoice', 'out_invoice')
           AND tax_line_id = tx_rep.invoice_tax_id
           AND tx_rep.repartition_type = 'tax'
    """
        % sql_dict
    )

    env["account.move.line"].invalidate_cache(fnames=["tax_repartition_line_id"])

    # We generate the migration dict, now that basic consistency of taxes is ensured
    migration_dicts_list = get_v13_migration_dicts(cr)
    # dict_fname = "/tmp/dict.mig"
    # if not os.path.isfile(dict_fname):
    #     migration_dicts_list = get_v13_migration_dicts(cr)
    #     with open(dict_fname, "wb") as f:
    #         pickle.dump(migration_dicts_list, f)
    # else:
    #     with open(dict_fname, "rb") as f:
    #         migration_dicts_list = pickle.load(f)

    # Assign tags and accounts to repartition lines
    for migration_dict in util.log_progress(migration_dicts_list, qualifier="taxes[repartition]"):
        if migration_dict["tax"]:
            tax = env["account.tax"].browse(migration_dict["tax"])
        else:
            tax = env["account.tax"]

        for rep_inv_type in ("invoice", "refund"):
            rep_vals = migration_dict[rep_inv_type]
            for rep_type, rep_tags in rep_vals.items():
                tags = []

                for tag_type, tag_details in rep_tags.items():
                    if tag_type == "financial":
                        tags += list(tag_details)
                    else:
                        to_add = env["account.account.tag"].search(
                            [
                                ("name", "in", [tag_type + name for name in tag_details]),
                                ("tax_negate", "=", (tag_type == "-")),
                                ("country_id", "=", tax.company_id.country_id.id),
                            ]
                        )

                        if len(to_add) != len(tag_details):
                            raise UserError(
                                "Missing tag. Some tag name is probably wrong. details: %(details)s  found tags: %(tags)s"
                                % {"details": str(tag_details), "tags": str(to_add)}
                            )

                        tags += to_add.ids

                if rep_type == "tax" and not (tax.amount_type in ("percent", "fixed") and tax.amount == 0):
                    rep_account_id = migration_dict[rep_inv_type == "invoice" and "inv_account_id" or "ref_account_id"]
                else:
                    rep_account_id = None

                getattr(tax, rep_inv_type + "_repartition_line_ids").filtered(
                    lambda x: x.repartition_type == rep_type
                ).write({"account_id": rep_account_id, "tag_ids": [(6, 0, tags)]})
    if not util.version_gte("saas~12.4"):
        # Assign repartition lines and tags to account.invoice.tax
        _logger.info("Migrating account.invoice.tax objects...")
        cr.execute(
            """
            UPDATE account_invoice_tax
               SET tax_repartition_line_id = tx_rep.id
              FROM account_tax_repartition_line tx_rep, account_invoice inv
             WHERE account_invoice_tax.invoice_id = inv.id
               AND account_invoice_tax.tax_id = case when inv.type in ('in_refund', 'out_refund')
                                             then tx_rep.refund_tax_id
                                             else tx_rep.invoice_tax_id end
               AND tx_rep.repartition_type = 'tax'
        """
        )
        env["account.invoice.tax"].invalidate_cache(fnames=["tax_repartition_line_id"])

        cr.execute(
            """
            INSERT INTO account_account_tag_account_invoice_tax_rel
                 SELECT inv_tx.id, rep_tag.account_account_tag_id
                   FROM account_invoice_tax inv_tx
                   JOIN account_account_tag_account_tax_repartition_line_rel rep_tag
                        ON inv_tx.tax_repartition_line_id = rep_tag.account_tax_repartition_line_id
        """
        )
        env["account.invoice.tax"].invalidate_cache(fnames=["tag_ids"])

    # Merge child taxes into their parent
    tax_groups = env["account.tax"].with_context(active_test=False).search([("amount_type", "=", "group")])

    # If some groups of tax have common children, they need to be migrated as groups of taxes
    # (since their tax aml are grouped, so we can't distinguish between them without re-posting the invoices)
    cr.execute(
        """
        SELECT array_agg(parent_tax)
          FROM account_tax_filiation_rel
      GROUP BY child_tax
        HAVING count(parent_tax) > 1
    """
    )
    taxes_not_to_merge = set()
    for (parent_taxes_list,) in cr.fetchall():
        taxes_not_to_merge.update(set(parent_taxes_list))

    # Some groups can be kept as groups in 12.3, for legal reasons
    cr.execute("SELECT tax_id FROM taxes_not_to_merge")
    taxes_not_to_merge.update({tax for (tax,) in cr.fetchall()})

    tax_to_clean_ids = []
    groups_to_merge = tax_groups.filtered(
        lambda x: x.id not in taxes_not_to_merge
        and all(
            child_tax.type_tax_use == "none" and child_tax.amount_type == "percent" for child_tax in x.children_tax_ids
        )
    )
    for group_to_treat in util.log_progress(groups_to_merge, qualifier="tax groups to merge"):
        # The tax repartition lines of the group are useless
        # (except if the have amount = 0, in wich case we keep them for simplicity)
        inv_tax_line = group_to_treat.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == "tax")
        ref_tax_line = group_to_treat.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == "tax")
        cr.execute(
            """
            UPDATE account_move_line
               SET tax_repartition_line_id=NULL
             WHERE tax_repartition_line_id in (%s,%s)
        """,
            (inv_tax_line.id, ref_tax_line.id),
        )
        env["account.move.line"].invalidate_cache(fnames=["tax_repartition_line_id"])

        group_to_treat.amount = _get_tax_group_percent(cr, group_to_treat)
        group_to_treat.amount_type = "percent"

        if (
            group_to_treat.amount != 0
        ):  # For 0-taxes, we keep the default empty ones, and remove all the reparition lines of child taxes.
            group_to_treat.write(
                {
                    "invoice_repartition_line_ids": [(2, inv_tax_line.id, 0)],
                    "refund_repartition_line_ids": [(2, ref_tax_line.id, 0)],
                }
            )

        # Changing the tax to which repartition lines belong will change the (now related) tax_line_id field of account.move.line
        group_inv_base_line = group_to_treat.invoice_repartition_line_ids.filtered(
            lambda x: x.repartition_type == "base"
        )
        group_ref_base_line = group_to_treat.refund_repartition_line_ids.filtered(
            lambda x: x.repartition_type == "base"
        )

        for child_tax in group_to_treat.children_tax_ids:
            new_inv_rep = child_tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == "tax")
            new_ref_rep = child_tax.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == "tax")

            if group_to_treat.amount != 0 and child_tax.amount != 0:
                new_inv_rep.invoice_tax_id = group_to_treat
                new_inv_rep.factor_percent = float_round(
                    100 * child_tax.amount / group_to_treat.amount, precision_digits=4
                )

                new_ref_rep.refund_tax_id = group_to_treat
                new_ref_rep.factor_percent = float_round(
                    100 * child_tax.amount / group_to_treat.amount, precision_digits=4
                )
            else:
                # If tax lines (aml with tax_line_id set, so) exist for 0% taxes (can
                # happen with POS), we remove the link to the tax if we have to merge them
                # (since these lines have no impact on the accounting). We avoid doing that
                # when not merging, just for the sake of not messing up with data uselessly.
                cr.execute(
                    """
                    UPDATE account_move_line
                       SET tax_repartition_line_id = null, tax_line_id = null
                     WHERE tax_repartition_line_id in %(rep_lines)s
                       AND balance = 0
                """,
                    {"rep_lines": (new_inv_rep.id, new_ref_rep.id)},
                )

                if not util.version_gte("saas~12.4"):
                    # account.invoice.tax for a 0% tax should never exist, they make no sense
                    # So, we delete them to avoid crashing the script later on
                    cr.execute(
                        """
                        DELETE FROM account_invoice_tax
                              WHERE tax_id = %(tax_to_delete)s
                    """,
                        {"tax_to_delete": child_tax.id},
                    )

                (new_inv_rep + new_ref_rep).unlink()

            # Child taxes also need to apply their base tags to their parent's base line
            group_inv_base_line.tag_ids |= child_tax.invoice_repartition_line_ids.filtered(
                lambda x: x.repartition_type == "base"
            ).tag_ids
            group_ref_base_line.tag_ids |= child_tax.refund_repartition_line_ids.filtered(
                lambda x: x.repartition_type == "base"
            ).tag_ids
            if not util.version_gte("saas~12.4"):
                # Before deleting the old child taxes, we also need to replace them on account.invoice.tax entries
                cr.execute(
                    """
                    UPDATE account_invoice_tax
                       SET tax_repartition_line_id = tx_rep.id, tax_id = %(group_to_treat_id)s
                      FROM account_invoice invoice, account_tax_repartition_line tx_rep
                     WHERE invoice.id = invoice_id
                       AND tax_id = %(child_tax_id)s
                       AND tx_rep.id = CASE WHEN invoice.type IN ('in_refund', 'out_refund')
                                       THEN %(new_ref_rep_id)s ELSE %(new_inv_rep_id)s END
                """,
                    {
                        "group_to_treat_id": group_to_treat.id,
                        "child_tax_id": child_tax.id,
                        "new_ref_rep_id": new_ref_rep.id,
                        "new_inv_rep_id": new_inv_rep.id,
                    },
                )

                # in case account.invoice.tax objects contain taxes to remove, we replace them by their parent
                cr.execute(
                    """
                    UPDATE account_invoice_tax_account_tax_rel
                       SET account_tax_id = %(group_to_treat_id)s
                     WHERE account_tax_id = %(child_tax_id)s
                """,
                    {"group_to_treat_id": group_to_treat.id, "child_tax_id": child_tax.id},
                )

                env["account.invoice.tax"].invalidate_cache(fnames=["tax_repartition_line_id", "tax_id", "tax_ids"])
            else:
                cr.execute(
                    """
                    UPDATE account_move_line
                       SET tax_line_id = %(group_to_treat_id)s
                     WHERE tax_line_id = %(child_tax_id)s
                """,
                    {"group_to_treat_id": group_to_treat.id, "child_tax_id": child_tax.id},
                )

        tax_to_clean_ids += list(group_to_treat.children_tax_ids.ids)

    if tax_to_clean_ids:
        cr.execute(
            """
            DELETE FROM account_fiscal_position_tax
            WHERE tax_src_id in %s or tax_dest_id in %s
        """,
            [tuple(tax_to_clean_ids), tuple(tax_to_clean_ids)],
        )
        cr.execute("DELETE FROM account_tax_filiation_rel WHERE child_tax in %s", [tuple(tax_to_clean_ids)])
        cr.execute("DELETE FROM account_tax WHERE id in %s", [tuple(tax_to_clean_ids)])
        cr.execute("DELETE FROM ir_model_data WHERE res_id in %s and model = 'account.tax';", [tuple(tax_to_clean_ids)])
        env["account.tax"].invalidate_cache()
        env["ir.model.data"].invalidate_cache()

    # Cleanup the tags on the groups that were kept (in case some were added due to weird 12.2 configuration)
    kept_groups = env["account.tax"].with_context(active_test=False).search([("amount_type", "=", "group")])
    for inv_type in ("invoice", "refund"):
        rep_lines = kept_groups.mapped(inv_type + "_repartition_line_ids")
        rep_lines.write({"tag_ids": [(5, 0, 0)]})

    # Add tags on account move lines

    # Tax lines
    _logger.info("Setting tags on tax amls...")
    cr.execute(
        """
        INSERT INTO account_account_tag_account_move_line_rel
             SELECT aml.id as account_move_line_id, rep_tags.account_account_tag_id as account_account_tag_id
               FROM account_move_line aml
               JOIN account_account_tag_account_tax_repartition_line_rel rep_tags
                    ON rep_tags.account_tax_repartition_line_id = aml.tax_repartition_line_id
    """
    )

    # Base lines
    _logger.info("Setting tags on base amls...")
    cr.execute(
        """
        INSERT INTO account_account_tag_account_move_line_rel
             SELECT aml_tx.account_move_line_id as account_move_line_id, rep_tags.account_account_tag_id as account_account_tag_id
               FROM account_tax_repartition_line tx_rep,
                    account_account_tag_account_tax_repartition_line_rel rep_tags,
                    account_move_line_account_tax_rel aml_tx
               JOIN account_move_line aml ON aml.id = aml_tx.account_move_line_id
               JOIN  %(invoice_table)s move ON aml.%(invoice_id_field)s = move.id
              WHERE tx_rep.repartition_type = 'base'
                AND aml_tx.account_tax_id = coalesce(tx_rep.invoice_tax_id, tx_rep.refund_tax_id)
                AND rep_tags.account_tax_repartition_line_id  = tx_rep.id
                AND ((move.type in ('in_refund', 'out_refund') AND tx_rep.refund_tax_id is not null)
                    OR (tx_rep.invoice_tax_id is not null and move.type IN ('in_invoice', 'out_invoice')))
        ON conflict do nothing; -- for lines that are the base of multiple taxes sharing some tags
    """
        % sql_dict
    )

    env["account.move.line"].invalidate_cache(fnames=["tag_ids"])

    # Basic consistency check for taxes associated with a template xmlid
    _logger.info("Consistency check")
    all_templates_data = env["ir.model.data"].search([("model", "=", "account.tax.template")])
    for tax_template_data in all_templates_data:
        tax_template = env["account.tax.template"].browse(tax_template_data.res_id)
        template_instance_data = env["ir.model.data"].search(
            [
                (
                    "name",
                    "=like",
                    r"%%\_%(name)s" % {"module": tax_template_data.module, "name": tax_template_data.name},
                ),
                ("model", "=", "account.tax"),
                ("module", "=", tax_template_data.module),
            ]
        )

        for data in template_instance_data:
            tax_instance = env["account.tax"].browse(data.res_id)

            if tax_template.amount_type != tax_instance.amount_type:
                _logger.warning(
                    "Tax template with id %s and instance with id %s don't have the same amount_type.",
                    tax_template.id,
                    tax_instance.id,
                )

            for inv_type in ("invoice", "refund"):
                tax_rep_lines = getattr(tax_instance, inv_type + "_repartition_line_ids")
                tax_accounts = sorted(tax_rep_lines.mapped("account_id.code"))
                tax_tags = sorted(tax_rep_lines.mapped("tag_ids.name"))

                # Some accounts have changed in generic COA in saas-12.5; also impacting tax repartition
                # For these, the migration script will keep the previous account when migrating
                # (of course, since only the template changes, not its instance).
                # In that case, the migration is correct, and the warning does not indicate any error.
                # We hardcode here an artificial switch of code for the two tax accounts
                # used in data of this module to avoid triggering the warning on runbot builds, with migration tests.
                # In case we add tests for localizations facing the same issues in the future, entries can be added to this dict.
                if util.version_gte("saas~12.5") and util.module_installed(cr, "l10n_generic_coa"):
                    acc_aliases = {
                        util.ref(cr, "l10n_generic_coa.tax_paid"): "1013",
                        util.ref(cr, "l10n_generic_coa.tax_received"): "1112",
                    }
                else:
                    acc_aliases = {}

                template_rep_lines = getattr(tax_template, inv_type + "_repartition_line_ids")
                account_codes_to_sort = []
                for account in template_rep_lines.mapped("account_id"):
                    acc_code = acc_aliases.get(account.id, account.code)
                    account_codes_to_sort.append(acc_code.ljust(account.chart_template_id.code_digits, "0"))

                template_accounts = sorted(account_codes_to_sort)
                template_tags = sorted(
                    set(
                        template_rep_lines.mapped("tag_ids.name")
                        + ["+" + tag for tag in template_rep_lines.mapped("plus_report_line_ids.tag_name")]
                        + ["-" + tag for tag in template_rep_lines.mapped("minus_report_line_ids.tag_name")]
                        + [tag for tag in template_rep_lines.mapped("tag_ids.name")]
                    )
                )

                # A tax template may have no tax repartition lines.
                # It should create a tax with default repartition (no account, no tag, only tax and base line)
                # Otherwize, repartition should be the same between template and tax.
                different_repartition = (
                    len(tax_rep_lines) != 2
                    if len(template_rep_lines) == 0
                    else len(template_rep_lines) != len(tax_rep_lines)
                )
                if different_repartition or template_accounts != tax_accounts or template_tags != tax_tags:
                    _logger.warning(
                        "Tax %s (id %s)'s %s repartition does not"
                        " seem to match its related template. Manual verification advised.",
                        tax_instance.id,
                        tax_instance.name,
                        inv_type,
                    )


def create_invoice(cr, partner, tax, amount=100, type="out_invoice"):
    """ Returns an open invoice """
    env = util.env(cr)
    base_domain = [
        ("company_id", "=", tax.company_id.id),
        ("deprecated", "=", False),
        "|",
        ("currency_id", "=", False),
        ("currency_id", "=", tax.company_id.currency_id.id),
    ]
    if util.version_gte("saas~12.4"):
        journal = (
            env["account.move"]
            .with_context(
                force_company=tax.company_id.id,
                default_company_id=tax.company_id.id,
                company_id=tax.company_id.id,
                default_type=type,
            )
            ._get_default_journal()
        )
    else:
        journal = (
            env["account.invoice"]
            .with_context(
                force_company=tax.company_id.id,
                default_company_id=tax.company_id.id,
                company_id=tax.company_id.id,
                type=type,
            )
            ._default_journal()
        )

    if not journal.id:
        _logger.error("Lack of suitable journal")
        return False

    if journal.type_control_ids or journal.account_control_ids:
        base_domain += [
            "|",
            ("user_type_id", "in", journal.type_control_ids.ids),
            ("id", "in", journal.account_control_ids.ids),
        ]
    invoice_line_account = (
        env["account.account"]
        .search(base_domain + [("user_type_id.type", "not in", ("payable", "receivable"))], limit=1)
        .id
    )
    if not invoice_line_account:
        _logger.error("Lack of suitable account")
        return False

    invoice = (
        env["account.move" if util.version_gte("saas~12.4") else "account.invoice"]
        .with_context(
            force_company=tax.company_id.id, default_company_id=tax.company_id.id, company_id=tax.company_id.id
        )
        .create(
            {
                "partner_id": partner.id,
                "currency_id": tax.company_id.currency_id.id,
                "type": type,
                "journal_id": journal.id,
                "invoice_date"
                if util.version_gte("saas~12.4")
                else "date_invoice": datetime.datetime.utcnow().isoformat(),
                "company_id": tax.company_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "quantity": 1,
                            "price_unit": amount,
                            "name": "Papa a vu le fifi de lolo",
                            "tax_ids" if util.version_gte("saas~12.4") else "invoice_line_tax_ids": [(6, 0, tax.ids)],
                            "account_id": invoice_line_account,
                        },
                    )
                ],
            }
        )
    )
    invoice_ctx = invoice.with_context(
        force_company=tax.company_id.id, default_company_id=tax.company_id.id, company_id=tax.company_id.id
    )
    if util.version_gte("saas~12.4"):
        invoice_ctx.post()
    else:
        invoice_ctx._onchange_invoice_line_ids()
        invoice_ctx.action_invoice_open()
    return invoice


def get_aml_domain(cr, invoice, domain):
    if util.version_gte("saas~12.4"):
        # invoice_id field does not exist anymore, use move_id instead
        domain = domain.replace(" ", "")
        domain = domain.replace("'notin'", "'not in'")
        domain = domain.replace("'notlike'", "'not like'")
        domain = domain.replace("'notilike'", "'not ilike'")
        domain = domain.replace(
            "('invoice_id','=',False)",
            "('move_id.type', 'not in', ('in_invoice', 'out_invoice', 'in_refund', 'out_refund'))",
        )
        domain = domain.replace("'invoice_id", "'move_id")

    line_domain = safe_eval(domain)

    # We need to use the backup table in order to know which tax corresponds to which tag
    for index, condition in enumerate(line_domain):
        if condition[0] in ("tax_ids.tag_ids", "tax_line_id.tag_ids"):

            if condition[1] not in ("=", "!=", "in", "not in"):
                raise UserError("Wrong operator in domain: %s" % condition[1])

            tag_values = condition[2]
            if isinstance(tag_values, list):
                tag_values = tuple(tag_values)

            cr.execute(
                """
                SELECT array_agg(account_tax_id)
                  FROM account_tax_account_tag_v12_bckp
                 WHERE account_account_tag_id """
                + condition[1]
                + """ %(values)s
            """,
                {"values": tag_values},
            )
            target_taxes = cr.fetchall()[0][0]

            line_domain[index] = (condition[0].partition(".")[0], "in", target_taxes or [])

    if util.version_gte("saas~12.4"):
        return line_domain + [("move_id.state", "=", "posted"), ("move_id", "=", invoice.id)]
    return line_domain + [("move_id.state", "=", "posted"), ("move_id", "=", invoice.move_id.id)]


def get_financial_reports_grids_mapping(cr):
    """ To be implemented specifically for each l10n_module.
    Returns a map between financial report line ids and the corresponding
    tax report line's tag_name in v13.
    """
    rslt = {}

    cr.execute(
        """
        SELECT lower(c.code)
          FROM account_tax_report_line l
          JOIN res_country c ON c.id = l.country_id
      GROUP BY 1
    """
    )
    for (cc,) in cr.fetchall():
        filler_fun_to_call = "_fill_grids_mapping_for_%s" % cc
        # So, such a function needs to be defined for each country
        if filler_fun_to_call not in globals():
            # Some countries don't have any tax report but some use financial reports instead, so
            # we still need to migrate.
            # XXX still needed?
            if cc not in "es ca cn co cr ec gt hk hn ie it mn mx nz pa pe pt sa tr ua us ve dk".split():
                raise util.MigrationError("Grids mapping not implemented for country %r" % cc)
        else:
            globals()[filler_fun_to_call](cr, rslt)

    return rslt


def _fill_grids_mapping_for_be(cr, dict_to_fill):
    code_prefix = "BETAX"
    cr.execute(
        """
        SELECT id, regexp_replace(code, '%(prefix)s', '')
          FROM financial_report_lines_v12_bckp
         WHERE code like '%(prefix)s%%'
           AND domain is not null
    """
        % {"prefix": code_prefix}
    )

    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_lu(cr, dict_to_fill):
    env = util.env(cr)
    # Fix inconsistent data in the v12 report, so that we can do things in a generic and clean way
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET code = 'LUTAX_b_SANS'
         WHERE code = 'b_SANS';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'II.D.2. taxe 17%'
         WHERE code = 'LUTAX_732';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'I.B.6.b)2) Prestations de services à des identifiés à la TVA dans '
                      'un autre Etat membre exonérées dans l''Etat membre du preneur (art.17/1/b)'
         WHERE code = 'LUTAX_424';
    """
    )

    # Merge the sublines that disappear in v13 with their parent, so that all the v12 domains correspond to the v13 tax report

    luxembourg_id = env["ir.model.data"].xmlid_to_res_id("base.lu")
    v13_tax_report_lines = env["account.tax.report.line"].search(
        [("country_id", "=", luxembourg_id), ("tag_name", "!=", None)]
    )

    # For report lines with childrens that are merged in a single line in v13,
    # Iterate on the children and map them all to the same v13 line

    cr.execute(
        """
        SELECT name, id, domain
          FROM financial_report_lines_v12_bckp
         WHERE code like 'LUTAX%%'
    """
    )
    lutax_lines_map = {entry["name"]: entry for entry in cr.dictfetchall()}
    for v13_line in v13_tax_report_lines:

        v12_line_data = lutax_lines_map.get(v13_line.name)
        if v12_line_data:

            if v12_line_data["domain"]:
                dict_to_fill[v12_line_data["id"]] = v13_line.tag_name
            else:
                # Then we need to treat its children (there is fortunately no
                # line merging children of childrens, so a simple loop is enough)
                cr.execute(
                    """
                    SELECT id
                      FROM financial_report_lines_v12_bckp
                     WHERE parent_id = %(parent_id)s
                """,
                    {"parent_id": v12_line_data["id"]},
                )
                for (child_id,) in cr.fetchall():
                    dict_to_fill[child_id] = v13_line.tag_name

        else:
            _logger.error("No V12 report line found with name %s", v13_line.name)


def _fill_grids_mapping_for_ae(cr, dict_to_fill):
    cr.execute(
        """
        SELECT name, id
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_ae%'
    """
    )
    name_map = dict(cr.fetchall())

    cr.execute(
        """
        SELECT code, id
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_ae%'
    """
    )
    code_map = dict(cr.fetchall())

    env = util.env(cr)
    ae_country_id = env["ir.model.data"].xmlid_to_res_id("base.ae")
    for line in env["account.tax.report.line"].search([("country_id", "=", ae_country_id), ("tag_name", "!=", False)]):
        matching_line = name_map.get(line.tag_name)

        if not matching_line and line.code:
            matching_line = code_map.get(line.code)

        if not matching_line:
            raise UserError(
                "l10n_ae: no financial report line found for tax report line %(name)s (id %(id)s)"
                % {"name": line.name, "id": line.id}
            )

        dict_to_fill[matching_line] = line.tag_name


def _fill_grids_mapping_for_ar(cr, dict_to_fill):
    cr.execute(
        """
        SELECT name, id
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_ar%'
    """
    )
    name_map = dict(cr.fetchall())

    env = util.env(cr)
    ar_country_id = env["ir.model.data"].xmlid_to_res_id("base.ar")
    for line in env["account.tax.report.line"].search([("country_id", "=", ar_country_id), ("tag_name", "!=", False)]):
        matching_line = name_map.get(line.tag_name)

        if not matching_line:
            raise UserError(
                "l10n_ar: no financial report line found for tax report line %(name)s (id %(id)s)"
                % {"name": line.name, "id": line.id}
            )

        dict_to_fill[matching_line] = line.tag_name


def _fill_grids_mapping_for_at(cr, dict_to_fill):
    # Manually assign the tag names for the lines with identical name
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET name = 'zum Steuersatz von 10 % (Innergemeinschaftliche Erwerbe - Steuerpflichtige Umsätze)'
         WHERE xmlid = 'account_financial_report_l10n_at_tva_line7';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'zum Steuersatz von 20 % (Innergemeinschaftliche Erwerbe - Steuerpflichtige Umsätze)'
         WHERE xmlid = 'account_financial_report_l10n_at_tva_line6';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'zum Steuersatz von 10% (Lieferungen, sonstige Leistungen und Eigenverbrauch - Steuerpflichtige Umsätze)'
         WHERE xmlid = 'account_financial_report_l10n_at_tva_line11';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'zum Steuersatz von 20 % (Lieferungen, sonstige Leistungen und Eigenverbrauch - Steuerpflichtige Umsätze)'
         WHERE xmlid = 'account_financial_report_l10n_at_tva_line10';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'zum Steuersatz von 20 % (Rechnungen von anderen Unternehmern und innergemeinschaftliche Dreiecksgeschäfte)'
         WHERE xmlid = 'account_financial_report_l10n_at_tva_line27';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'zum Steuersatz von 10 % (Rechnungen von anderen Unternehmern und innergemeinschaftliche Dreiecksgeschäfte)'
         WHERE xmlid = 'account_financial_report_l10n_at_tva_line26';
    """
    )

    code_prefix = "ATT"
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE code like '%(prefix)s%%'
           AND domain is not null
    """
        % {"prefix": code_prefix}
    )

    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_au(cr, dict_to_fill):
    env = util.env(cr)
    au_companies = env["res.company"].search([("partner_id.country_id.code", "=", "AU")])
    cr.execute(
        """
        SELECT distinct account_account_tag_id
          FROM account_tax_account_tag_v12_bckp
          JOIN tax_accounts_v12_bckp
               ON tax_accounts_v12_bckp.id = account_tax_account_tag_v12_bckp.account_tax_id
          JOIN account_tax
               ON account_tax.id = account_tax_account_tag_v12_bckp.account_tax_id
         WHERE tax_accounts_v12_bckp.account_id is not null
           AND account_tax.company_id in %(company_ids)s
    """,
        {"company_ids": tuple(au_companies.ids)},
    )
    all_tags = [tag for (tag,) in cr.fetchall()]
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET domain = %(domain)s
         WHERE xmlid = 'account_financial_report_l10n_au_gstrpt_c_gl'
    """,
        {"domain": "[('tax_line_id.tag_ids', 'in', %s)]" % str(all_tags)},
    )
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET code = 'GST from General Ledger'
         WHERE xmlid = 'account_financial_report_l10n_au_gstrpt_c_gl'
    """
    )
    cr.execute(
        """
        SELECT id, code
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_au_gstrpt%'
           AND domain is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_bo(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_bo%'
           AND domain is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_br(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_br%'
           AND domain is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_ch(cr, dict_to_fill):
    # Lines 311a and 311b have been replaced by 312a and 312b; so we simply
    # give them the same name here to fetch the same tags during migration.
    # 382a_200 has been entirely removed and should be ignored
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET name = '312a Chiffre d''affaires imposable a 2.5% (TR)'
         WHERE xmlid = 'financial_report_line_chtax_311a'
           AND module = 'l10n_ch_reports';

        UPDATE financial_report_lines_v12_bckp
           SET name = '312b TVA due a 2.5% (TR)'
         WHERE xmlid = 'financial_report_line_chtax_311b'
           AND module = 'l10n_ch_reports';

        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'financial_report_line_chtax%'
           AND xmlid != 'financial_report_line_chtax_382a_200'
           AND domain is not null
           AND module = 'l10n_ch_reports';
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_cl(cr, dict_to_fill):
    cr.execute(
        """
        SELECT financial_report_lines_v12_bckp.id, account_tax_report_line.tag_name
          FROM financial_report_lines_v12_bckp
          JOIN account_tax_report_line
               ON account_tax_report_line.name = CASE
                   WHEN xmlid = 'financial_report_line_cl_030101' THEN 'Ventas Netas Gravadas con IVA'
                   WHEN xmlid = 'financial_report_line_cl_030102' THEN 'Ventas Exentas'
                   WHEN xmlid = 'financial_report_line_cl_020201' THEN 'IVA Debito Fiscal'
                   WHEN xmlid = 'financial_report_line_cl_030201' THEN 'Compras Netas Gravadas Con IVA (recuperable)'
                   WHEN xmlid = 'financial_report_line_cl_030202' THEN 'Compras No Gravadas Con Iva'
                   WHEN xmlid = 'financial_report_line_cl_020101' THEN 'IVA Pagado Compras Recuperables'
                   WHEN xmlid = 'financial_report_line_cl_020203' THEN 'Compras Iva No Recuperable'
                   ELSE financial_report_lines_v12_bckp.name
               END
         WHERE financial_report_lines_v12_bckp.xmlid like 'financial_report_line_cl%'
           AND financial_report_lines_v12_bckp.module = 'l10n_cl_reports'
           AND financial_report_lines_v12_bckp.domain is not null
           AND financial_report_lines_v12_bckp.formulas is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_de(cr, dict_to_fill):
    env = util.env(cr)
    germany_id = env["ir.model.data"].xmlid_to_res_id("base.de")
    v13_tax_report_line_tag_names = (
        env["account.tax.report.line"]
        .search([("country_id", "=", germany_id), ("tag_name", "!=", None)])
        .mapped("tag_name")
    )
    cr.execute(
        """
        SELECT id, SPLIT_PART(name,'.',1) as name, xmlid
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'financial_report_line_de%'
           AND domain is not null
    """
    )
    for v12_line in cr.dictfetchall():
        name = v12_line["name"] + (v12_line["xmlid"].find("_base") > 0 and "_BASE" or "_TAX")
        if name not in v13_tax_report_line_tag_names:
            name = v12_line["name"]
        dict_to_fill.update({v12_line["id"]: name})


def _fill_grids_mapping_for_do(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, SPLIT_PART(name,' ',1)
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like '%_do'
           AND domain is not null
           AND module = 'l10n_do_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_et(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like '%_et'
           AND domain is not null
           AND module = 'l10n_et_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_fr(cr, dict_to_fill):
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET domain=NULL
         WHERE xmlid = 'account_financial_report_line_98_fr'
           AND module = 'l10n_fr_reports';

        UPDATE financial_report_lines_v12_bckp
           SET name='Base H.T. 5.5%'
         WHERE xmlid = 'account_financial_report_line_08_fr'
           AND module = 'l10n_fr_reports';

        UPDATE financial_report_lines_v12_bckp
           SET name='Base H.T. 5.5%'
         WHERE xmlid = 'account_financial_report_line_08_fr'
           AND module = 'l10n_fr_reports';
    """
    )

    cr.execute(
        """
        SELECT sub.id,
            CASE WHEN sub.parent_name = 'Base H.T. TVA collectée'
                      THEN replace(sub.name,'H.T.','collectée')
                 WHEN sub.parent_name = 'TVA collectée'
                      THEN replace(sub.name,'TVA','TVA collectée')
                 WHEN sub.parent_name = 'Base H.T. TVA acquittée'
                      THEN replace(sub.name,'H.T.','acquittée')
                 WHEN sub.parent_name = 'TVA acquittée'
                      THEN replace(sub.name,'TVA','TVA acquittée')
                 WHEN sub.parent_name = 'Base H.T. TVA acquittée pour immobilisations'
                      THEN replace(sub.name,'H.T.','acquittée immo.')
                 WHEN sub.parent_name = 'TVA acquittée pour immobilisations'
                      THEN replace(sub.name,'TVA','TVA acquittée immo.')
                 WHEN sub.parent_name = 'Base H.T. TVA due intracommunautaire'
                      THEN replace(sub.name,'H.T.','due intracom.')
                 WHEN sub.parent_name = 'TVA due intracommunautaire'
                      THEN replace(sub.name,'TVA','TVA due intracom.')
                 WHEN sub.parent_name = 'Base H.T. TVA déductible intracommunautaire'
                      THEN replace(sub.name,'H.T.','déductible intracom.')
                 WHEN sub.parent_name = 'TVA déductible intracommunautaire'
                      THEN replace(sub.name,'TVA','TVA déductible intracom.')
            ELSE name
            END as tag_name
        FROM (SELECT id, name,
                     (SELECT name
                        FROM financial_report_lines_v12_bckp rlv12_parent
                       WHERE rlv12_parent.id = rlv12.parent_id) as parent_name
                FROM financial_report_lines_v12_bckp rlv12
               WHERE xmlid LIKE '%_fr'
                 AND domain IS NOT NULL
        ) as sub
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_gr(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_si%'
           AND domain is not null
           AND module = 'l10n_gr_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_hr(cr, dict_to_fill):
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET name = replace(name,' bis', ' (30%)')
         WHERE xmlid = 'financial_report_l10n_hr_line_66b';

        UPDATE financial_report_lines_v12_bckp
           SET name = replace(name,' bis', ' (70%)')
         WHERE xmlid = 'financial_report_l10n_hr_line_23b';

        UPDATE financial_report_lines_v12_bckp
           SET name = replace(name,' ter', ' (30%)')
         WHERE xmlid = 'financial_report_l10n_hr_line_23t';

        UPDATE financial_report_lines_v12_bckp
           SET name = replace(name,' ter', ' (70%)')
         WHERE xmlid = 'financial_report_l10n_hr_line_66t';

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (osnovica)')
         WHERE xmlid in ('financial_report_l10n_hr_line_15',
                         'financial_report_l10n_hr_line_17',
                         'financial_report_l10n_hr_line_21',
                         'financial_report_l10n_hr_line_24',
                         'financial_report_l10n_hr_line_26',
                         'financial_report_l10n_hr_line_28');

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (porez)')
         WHERE xmlid in ('financial_report_l10n_hr_line_34',
                         'financial_report_l10n_hr_line_36',
                         'financial_report_l10n_hr_line_40',
                         'financial_report_l10n_hr_line_43',
                         'financial_report_l10n_hr_line_44',
                         'financial_report_l10n_hr_line_46');

        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = sum.balance'
         WHERE xmlid = 'financial_report_l10n_hr_line_66';
    """
    )

    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'financial_report_l10n_hr%'
           AND domain is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_hu(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'financial_report_line_hu%'
           AND domain is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_in(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like '%l10n_in_line%'
           AND domain is not null;
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_jp(cr, dict_to_fill):
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET name = '不課税 (仮受税額)'
         WHERE xmlid = 'account_financial_report_l10n_jp_line_4'
           AND module = 'l10n_jp_reports';

        UPDATE financial_report_lines_v12_bckp
           SET name = '不課税 (仮払税額)'
         WHERE xmlid = 'account_financial_report_l10n_jp_line_8'
           AND module = 'l10n_jp_reports';
    """
    )

    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_jp_line%'
           AND domain is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_ma(cr, dict_to_fill):
    """old tax line use domain and sum formula so split line in V13 so here replace with domain value string"""

    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET name='Achats à l''importation (10%) (HT)'
         WHERE xmlid = 'account_financial_report_l10n_ma_line_102';

        UPDATE financial_report_lines_v12_bckp
           SET name='Achats à l''importation (10%) (TVA)'
         WHERE xmlid = 'account_financial_report_l10n_ma_line_117';

        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = -sum.balance'
         WHERE xmlid in ('account_financial_report_l10n_ma_line_8',
                        'account_financial_report_l10n_ma_line_14',
                        'account_financial_report_l10n_ma_line_20',
                        'account_financial_report_l10n_ma_line_30',
                        'account_financial_report_l10n_ma_line_40',
                        'account_financial_report_l10n_ma_line_54',
                        'account_financial_report_l10n_ma_line_68',
                        'account_financial_report_l10n_ma_line_84')
           AND module = 'l10n_ma_reports';

        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = sum.balance'
         WHERE xmlid in ('account_financial_report_l10n_ma_line_102',
                        'account_financial_report_l10n_ma_line_117',
                        'account_financial_report_l10n_ma_line_129',
                        'account_financial_report_l10n_ma_line_137')
           AND module = 'l10n_ma_reports';
        """
    )
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_ma%'
           AND domain is not null;
    """
    )

    for id, name in cr.fetchall():
        """Update tag name in v13 so replace with new update string"""
        if name.find("-Achat") >= 0:
            name = name.replace("-Achat", "Achat")
        if name.find("2-IMMOBILISATIONS") >= 0:
            name = name.replace("2-IMMOBILISATIONS", "Immobilisations")
        dict_to_fill.update(dict([(id, name)]))


def _fill_grids_mapping_for_nl(cr, dict_to_fill):
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = -sum.balance'
         WHERE xmlid in ('financial_report_line_nl_01_01_01',
                        'financial_report_line_nl_02_01_01',
                        'financial_report_line_nl_02_03_02',
                        'financial_report_line_nl_02_03_01')
           AND module = 'l10n_nl_reports';
    """
    )

    cr.execute(
        """
        SELECT financial_report_lines_v12_bckp.id, account_tax_report_line.tag_name
          FROM financial_report_lines_v12_bckp
          JOIN account_tax_report_line
            ON account_tax_report_line.name =
                CASE WHEN xmlid = 'financial_report_line_nl_01_01_01_01'
                        THEN '1a. Leveringen/diensten belast met hoog tarief (omzet)'
                     WHEN xmlid = 'financial_report_line_nl_02_01_01_01'
                        THEN '1a. Leveringen/diensten belast met 21% (BTW)'
                ELSE financial_report_lines_v12_bckp.name
                END
         WHERE financial_report_lines_v12_bckp.xmlid like 'financial_report_line_nl%'
           AND financial_report_lines_v12_bckp.module = 'l10n_nl_reports'
           AND financial_report_lines_v12_bckp.domain is not null
           AND financial_report_lines_v12_bckp.formulas is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_no(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'financial_report_no_%'
           AND domain is not null
           AND module = 'l10n_no_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_pl(cr, dict_to_fill):
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = sum.balance'
         WHERE xmlid in ('account_financial_report_pl_03_01_01_04_04',
                         'account_financial_report_pl_02_02',
                         'account_financial_report_pl_01_12')
           AND module = 'l10n_pl_reports'
    """
    )

    cr.execute(
        """
        SELECT financial_report_lines_v12_bckp.id, account_tax_report_line.tag_name
          FROM financial_report_lines_v12_bckp
          JOIN account_tax_report_line
            ON account_tax_report_line.name =
                CASE WHEN xmlid = 'account_financial_report_pl_03_01_01_04_04b'
                        THEN 'Podatek - Nabycie towarów i usług pozostałych'
                     WHEN xmlid = 'account_financial_report_pl_02_02b'
                        THEN 'Podstawa - Nabycie towarów i usług pozostałych'
                     WHEN xmlid = 'account_financial_report_pl_01_12b'
                        THEN 'Podstawa - Dostawa towarów, podatnik nabywca'
                ELSE financial_report_lines_v12_bckp.name
                END
         WHERE financial_report_lines_v12_bckp.xmlid like 'account_financial_report_pl_%'
           AND financial_report_lines_v12_bckp.module = 'l10n_pl_reports'
           AND financial_report_lines_v12_bckp.domain is not null
           AND financial_report_lines_v12_bckp.formulas is not null;
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_ro(cr, dict_to_fill):
    cr.execute(
        r"""
        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (TVA colectata)')
         WHERE code like 'ROTAX_TVA_colectata%'
           AND name not like 'Baza TVA%';

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (deductibila)')
         WHERE code like 'ROTAX_TVA_deductibila%'
           AND (name not like '%_i%%'
            OR name = 'TVA Intracomunitar Bunuri');

        UPDATE financial_report_lines_v12_bckp
           SET name = 'Baza TVA Intracomunitar Servicii (deductibila)'
         WHERE name = 'Baza TVA Intracomunitar Servicii%';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'Baza TVA Intracomunitar Bunuri (deductibila)'
         WHERE name = 'Baza TVA Intracomunitar Bunuri%';

        UPDATE financial_report_lines_v12_bckp
           SET name = 'Baza TVA Taxare Inversa (deductibila)'
         WHERE name = 'Baza TVA Taxare Inversa'
           AND xmlid like 'account\_tax\_report\_ro\_%';
    """
    )

    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_ro%'
           AND domain is not null
           AND module = 'l10n_ro_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_sg(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, SPLIT_PART(name,' - ',1) as name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'account_financial_report_l10n_sg_gst_returns%'
           AND domain is not null;
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_si(cr, dict_to_fill):
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = -sum.balance'
         WHERE xmlid in ('financial_report_line_si_02020102',
                         'financial_report_line_si_02020101')
           AND module = 'l10n_si_reports';

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (Neodbitni)')
         WHERE module = 'l10n_si_reports'
           AND xmlid in ('financial_report_line_si_01010101',
                         'financial_report_line_si_01010102');

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (Vstopni)')
         WHERE module = 'l10n_si_reports'
           AND xmlid in ('financial_report_line_si_01020202',
                         'financial_report_line_si_01020203');
    """
    )

    cr.execute(
        """
        SELECT financial_report_lines_v12_bckp.id, account_tax_report_line.tag_name
          FROM financial_report_lines_v12_bckp
          JOIN account_tax_report_line
            ON account_tax_report_line.tag_name =
                CASE WHEN xmlid = 'financial_report_line_si_02020102b'
                        THEN 'Izstopni DDV - znižana stopnja'
                     WHEN xmlid = 'financial_report_line_si_02020101b'
                        THEN 'Izstopni DDV - osnovna stopnja'
                ELSE financial_report_lines_v12_bckp.name
                END
         WHERE financial_report_lines_v12_bckp.xmlid like 'financial_report_line_si%'
           AND financial_report_lines_v12_bckp.module = 'l10n_si_reports'
           AND financial_report_lines_v12_bckp.domain is not null
           AND financial_report_lines_v12_bckp.formulas is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_th(cr, dict_to_fill):
    tag_id = util.env(cr)["ir.model.data"].xmlid_to_res_id("l10n_th.tag_th_05")
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET domain = '[(''tax_line_id.tag_ids'', ''in'', [%(tag_id)s])]'
         WHERE xmlid = 'account_financial_report_th_01_2'
           AND module = 'l10n_th_reports';

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (to be paid)')
         WHERE module = 'l10n_th_reports'
           AND xmlid in ('account_financial_report_th_02_1',
                         'account_financial_report_th_02_2',
                         'account_financial_report_th_01_1',
                         'account_financial_report_l10n_th_03',
                         'account_financial_report_l10n_th_04');

        UPDATE financial_report_lines_v12_bckp
           SET name = concat(name, ' (taxable)')
         WHERE module = 'l10n_th_reports'
           AND xmlid in ('account_financial_report_th_2_1_2_1',
                         'account_financial_report_th_2_1_2_2',
                         'account_financial_report_th_2_1_1_1',
                         'account_financial_report_th_2_2_1',
                         'account_financial_report_th_2_2_2');
    """,
        {"tag_id": tag_id},
    )

    cr.execute(
        """
        SELECT id, SPLIT_PART(name,' - ',1) as name
          FROM financial_report_lines_v12_bckp
         WHERE code like 'THTAX%'
           AND domain is not null
           AND module = 'l10n_th_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_gb(cr, dict_to_fill):  # For some reason, UK's country code is GB...
    env = util.env(cr)
    ref = env["ir.model.data"].xmlid_to_res_id
    grid_7_domain = [
        (
            "tax_ids.tag_ids",
            "in",
            [
                ref("l10n_uk.tag_pt11"),
                ref("l10n_uk.tag_pt5"),
                ref("l10n_uk.tag_pt2"),
                ref("l10n_uk.tag_pt1"),
                ref("l10n_uk.tag_pt0"),
                ref("l10n_uk.tag_pt7"),
                ref("l10n_uk.tag_pt8"),
            ],
        )
    ]
    grid_6_domain = [
        (
            "tax_ids.tag_ids",
            "in",
            [
                ref("l10n_uk.tag_st0"),
                ref("l10n_uk.tag_st1"),
                ref("l10n_uk.tag_st2"),
                ref("l10n_uk.tag_st11"),
                ref("l10n_uk.tag_st4"),
            ],
        )
    ]

    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = sum.balance'
         WHERE xmlid in ('financial_report_line_uk_0103',
                         'financial_report_line_uk_03')
           AND module = 'l10n_uk_reports';

        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = -sum.balance'
         WHERE xmlid in ('financial_report_line_uk_02')
           AND module = 'l10n_uk_reports';

        UPDATE financial_report_lines_v12_bckp
           SET domain = %(grid_6_domain)s
         WHERE xmlid in ('financial_report_line_uk_02')
           AND module = 'l10n_uk_reports';

        UPDATE financial_report_lines_v12_bckp
           SET domain = %(grid_7_domain)s
         WHERE xmlid in ('financial_report_line_uk_03')
           AND module = 'l10n_uk_reports';

        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = -sum.balance'
         WHERE xmlid in ('financial_report_line_uk_0103b')
           AND module = 'l10n_uk_reports';
    """,
        {"grid_6_domain": str(grid_6_domain), "grid_7_domain": str(grid_7_domain)},
    )

    cr.execute(
        """
        SELECT financial_report_lines_v12_bckp.id, account_tax_report_line.tag_name
          FROM financial_report_lines_v12_bckp
          JOIN account_tax_report_line
               ON account_tax_report_line.tag_name = CASE WHEN xmlid = 'financial_report_line_uk_0103b' THEN '4'
                                                          ELSE replace(financial_report_lines_v12_bckp.code, 'UKTAX_', '') END
         WHERE financial_report_lines_v12_bckp.xmlid like 'financial_report_line_uk%'
           AND financial_report_lines_v12_bckp.module = 'l10n_uk_reports'
           AND financial_report_lines_v12_bckp.domain is not null
           AND financial_report_lines_v12_bckp.formulas is not null
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_uy(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like '%_uy'
           AND domain is not null
           AND module = 'l10n_uy_reports';
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_vn(cr, dict_to_fill):
    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like '%_vn'
           AND domain is not null
           AND module = 'l10n_vn_reports'
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def _fill_grids_mapping_for_za(cr, dict_to_fill):
    env = util.env(cr)
    ref = env["ir.model.data"].xmlid_to_res_id
    vat10_domain = [
        "|",
        ("tax_ids.tag_ids", "in", [ref("l10n_za.tag_ST10")]),
        ("tax_line_id.tag_ids", "in", [ref("l10n_za.tag_ST10")]),
    ]
    cr.execute(
        """
        UPDATE financial_report_lines_v12_bckp
           SET formulas = 'balance = -sum.balance', domain = %(vat10_domain)s
         WHERE xmlid in ('za_vat_financial_report_line_18')
           AND module = 'l10n_za_reports';
    """,
        {"vat10_domain": str(vat10_domain)},
    )

    cr.execute(
        """
        SELECT id, name
          FROM financial_report_lines_v12_bckp
         WHERE xmlid like 'za_vat_financial_report_line%'
           AND domain is not null
           AND formulas is not null
           AND module = 'l10n_za_reports';
    """
    )
    dict_to_fill.update(dict(cr.fetchall()))


def erase_edi_data(cr):
    """ Erases all edi data defined by the installed modules, so that we can
    create test invoices to check taxes repartition without sending them to the
    goverment.
    The operations made by this function need of course to be rollbacked.
    """
    if util.module_installed(cr, "l10n_co_edi"):
        cr.execute(
            """
            UPDATE res_company
               SET l10n_co_edi_test_mode = true;
        """
        )
    if util.module_installed(cr, "l10n_mx_edi"):
        cr.execute(
            """
            UPDATE res_company
               SET l10n_mx_edi_pac_test_env = true;
        """
        )
    if util.module_installed(cr, "l10n_it_edi"):
        cr.execute(
            """
            DELETE FROM ir_mail_server;

            UPDATE res_partner
               SET country_id = null
              FROM res_country
             WHERE res_country.id = res_partner.country_id
               AND res_country.code = 'IT';
        """
        )


def get_v13_migration_dicts(cr):
    """
    TO BE RETURNED

    [{'tax': tax,
      'inv_account_id': acc1,
      'ref_account_id': acc2,
      'invoice': {'base': {'+': set<tag_names>,
                           '-': set<tag_names>,
                           'financial': set<tag_ids>}
                          },
                  'refund': {'tax': {'-': set<tag_names>}}},
    ... other taxes ...]
    """
    cr.execute("savepoint v13_migration_dict;")

    env = util.env(cr)

    # Set all taxes as active ; keep track of the inactive ones to restore their state later

    cr.execute("UPDATE account_tax SET active=true")

    env["account.tax"].invalidate_cache(fnames=["active"])

    # If a tax is type_tax_use 'none', we artificially switch it to its parent
    # type temporarily, to check what grids to impact for it
    cr.execute(
        """
        UPDATE account_tax
           SET type_tax_use = parent.type_tax_use, name = concat(account_tax.name, account_tax.id::varchar)
          FROM account_tax_filiation_rel tx_rel, account_tax parent
         WHERE tx_rel.child_tax = account_tax.id
           AND parent.id = tx_rel.parent_tax
           AND account_tax.type_tax_use = 'none';
    """
    )  # Groups with type_tax_use = 'none' are not supported, so no group of group here

    env["account.tax"].invalidate_cache(fnames=["type_tax_use"])

    # To properly migrate adjustment taxes, we need to male sure they create tax lines when used
    cr.execute("UPDATE account_tax set amount=10 WHERE amount=0 AND type_tax_use = 'adjustment'")

    partner = env["res.partner"].create({"name": "Tax migrator"})

    tax_line_selector = lambda x: x.tax_line_id
    base_line_selector = (
        lambda x: x.tax_ids and not x.tax_line_id
    )  # tax_ids and tax_line_id are set together for tax lines affected by previous taxes

    financial_reports_grids_mapping = get_financial_reports_grids_mapping(cr)

    erase_edi_data(cr)
    env["res.company"].invalidate_cache()
    env["res.partner"].invalidate_cache(fnames=["country_id"])

    # Get all the financial tags defined in 12.3
    cr.execute(
        """
        SELECT tag_id
          FROM v12_financial_tags_registry
    """
    )
    #  This query only fetches the tags still declared, not the former ones, since the module has now been UPDATEd
    financial_tag_ids = {elem for (elem,) in cr.fetchall()}

    rslt = []
    cr.execute(
        """
        SELECT account_tax.id, case when count(account_account_tag_id) > 0 then array_agg(account_account_tag_id) else '{}' end
          FROM account_tax
     LEFT JOIN account_tax_account_tag_v12_bckp
               ON account_tax.id = account_tax_account_tag_v12_bckp.account_tax_id
      GROUP BY account_tax.id
    """
    )
    for tax_id, tax_tag_ids in util.log_progress(cr.fetchall(), qualifier="taxes"):
        tax = env["account.tax"].browse(tax_id)

        # get account_id and refund_account_id in SQL, since they have been removed between 12.2 and 12.3
        cr.execute(
            """
            SELECT account_id, refund_account_id
              FROM tax_accounts_v12_bckp
             WHERE id=%(tax_id)s;
        """,
            {"tax_id": tax_id},
        )
        tax_accounts_dict = cr.dictfetchall()[0]

        tax_rslt = {
            "tax": tax.id,
            "invoice": {
                "base": {"+": set(), "-": set(), "financial": set()},
                "tax": {"+": set(), "-": set(), "financial": set()},
            },
            "refund": {
                "base": {"+": set(), "-": set(), "financial": set()},
                "tax": {"+": set(), "-": set(), "financial": set()},
            },
            "inv_account_id": tax_accounts_dict["account_id"],
            "ref_account_id": tax_accounts_dict["refund_account_id"],
        }
        rslt.append(tax_rslt)

        inv = create_invoice(cr, partner, tax, type=tax.type_tax_use == "sale" and "out_invoice" or "in_invoice")

        ref = create_invoice(cr, partner, tax, type=tax.type_tax_use == "sale" and "out_refund" or "in_refund")

        if inv and ref:
            for tag_id in tax_tag_ids:
                is_financial = tag_id in financial_tag_ids

                # We want to see where v12 tags go, in order to prepare v13 tags assignation
                cr.execute(
                    r"""
                    SELECT id, domain, formulas
                      FROM financial_report_lines_v12_bckp
                     WHERE domain like '%%tax%%.tag\_ids%%%(tag_id)s%%'
                    """,
                    {"tag_id": tag_id},
                )
                tag_report_lines_data = cr.fetchall()

                if not tag_report_lines_data:
                    _logger.warning(
                        "No financial report line found for tag with id %s. Is it normal?", tag_id,
                    )

                for tax_report_line_id, domain, formulas in tag_report_lines_data:

                    # aml considered by this report line for both invoice and refund
                    inv_aml = env["account.move.line"].search(get_aml_domain(cr, inv, domain))
                    ref_aml = env["account.move.line"].search(get_aml_domain(cr, ref, domain))

                    # Treat tax lines
                    inv_tax_line = inv_aml.filtered(
                        tax_line_selector
                    )  # if len > 1, it's weird, so we let it crash later
                    ref_tax_line = ref_aml.filtered(tax_line_selector)

                    split_formula = _split_formulas_to_dict(cr, formulas)

                    if (
                        tax.type_tax_use == "adjustment"
                        and tax_report_line_id in financial_reports_grids_mapping
                        and (inv_tax_line or ref_tax_line)
                    ):  # We treat tax adjustment in a dedicated way, as they are not supposed to be used on invoices
                        tax_rslt["invoice"]["tax"]["+"].add(financial_reports_grids_mapping[tax_report_line_id])
                        tax_rslt["refund"]["tax"]["-"].add(financial_reports_grids_mapping[tax_report_line_id])
                        continue

                    candidate_to_add = (
                        is_financial and tag_id or financial_reports_grids_mapping.get(tax_report_line_id)
                    )

                    if not candidate_to_add:
                        # Happens for noisy financial report lines, not corresponding to any tax report.
                        # We can't remove these lines from the backup table with 100% certainty; we would
                        # risk to remove lines using financial tags
                        continue

                    if (
                        tax.amount != 0 or tax.amount_type == "code"
                    ):  # We don't want tags on taxes whose tax amount is 0
                        # (there could be without this condition, depending on 12.2 setup)

                        if inv_tax_line:
                            if len(inv_tax_line) > 1:
                                inv_tax_line = inv_tax_line[0]  # May happen for groups

                            formula_evaluator = lambda: (tax.amount < 0 and -1 or 1) * safe_eval(
                                split_formula["balance"], {"sum": inv_tax_line}
                            )
                            _add_repartition_to_tax_dict(
                                cr, "invoice", "tax", tax_rslt, candidate_to_add, is_financial, formula_evaluator
                            )
                        if ref_tax_line:
                            if len(ref_tax_line) > 1:
                                ref_tax_line = ref_tax_line[0]  # May happen for groups

                            formula_evaluator = lambda: (tax.amount < 0 and -1 or 1) * safe_eval(
                                split_formula["balance"], {"sum": ref_tax_line}
                            )
                            _add_repartition_to_tax_dict(
                                cr, "refund", "tax", tax_rslt, candidate_to_add, is_financial, formula_evaluator
                            )

                    # Treat base lines
                    inv_base_line = inv_aml.filtered(base_line_selector)
                    ref_base_line = ref_aml.filtered(base_line_selector)

                    if inv_base_line:
                        formula_evaluator = lambda: safe_eval(split_formula["balance"], {"sum": inv_base_line})
                        _add_repartition_to_tax_dict(
                            cr, "invoice", "base", tax_rslt, candidate_to_add, is_financial, formula_evaluator
                        )
                    if ref_base_line:
                        formula_evaluator = lambda: safe_eval(split_formula["balance"], {"sum": ref_base_line})
                        _add_repartition_to_tax_dict(
                            cr, "refund", "base", tax_rslt, candidate_to_add, is_financial, formula_evaluator
                        )
        else:
            _logger.error("Cannot create invoice (lack of suitable account) for tax %s", tax_id)

    # Convert financial tags
    _convert_financial_tags(cr, rslt)

    cr.execute("rollback to savepoint v13_migration_dict;")
    env.clear()  # Reset the cache because of the rollback that just occured

    return rslt


def _get_financial_tags_conversion_map(cr):
    # Returns a dictionary mapping the financial tags that need to be converted to
    # other tags to these new tags, and giving the conditions for this replacement
    cr.execute(
        """
        SELECT old_data.res_id as old_tag_id, invoice_type, repartition_type, new_data.res_id as new_tag_id
          FROM financial_tags_conversion_map conv_map
          JOIN ir_model_data old_data ON old_data.name = conv_map.old_tag_name AND old_data.module = conv_map.module
          JOIN ir_model_data new_data ON new_data.name = conv_map.new_tag_name AND new_data.module = conv_map.module
    """
    )

    rslt = {}
    for conv_data in cr.dictfetchall():
        tag_map = rslt.get(conv_data["old_tag_id"])
        if not tag_map:
            tag_map = {}
            rslt[conv_data["old_tag_id"]] = tag_map

        inv_type_data = tag_map.get(conv_data["invoice_type"])
        if not inv_type_data:
            inv_type_data = {}
            tag_map[conv_data["invoice_type"]] = inv_type_data

        inv_type_data[conv_data["repartition_type"]] = conv_data["new_tag_id"]

    return rslt


def _convert_financial_tags(cr, mig_dicts_list):
    # Apply conversion to the financial tags, in case some of them were removed
    # and replaced by other tags in 12.3 (like for l10n_es)
    tags_conversion_map = _get_financial_tags_conversion_map(cr)
    for mig_dict in mig_dicts_list:
        for inv_type in ("invoice", "refund"):
            for rep_type, rep_vals in mig_dict[inv_type].items():
                original_set = rep_vals["financial"].copy()
                for tag_id in original_set:
                    tag_conversion = tags_conversion_map.get(tag_id)
                    replacement = tag_conversion and tag_conversion.get(inv_type, {}).get(rep_type)
                    if replacement:
                        rep_vals["financial"].remove(tag_id)
                        rep_vals["financial"].add(replacement)


def _add_repartition_to_tax_dict(cr, inv_type, rep_type, tax_dict, to_add, is_financial, formula_evaluator):
    rep_key = is_financial and "financial" or (formula_evaluator() < 0 and "-" or "+")
    tax_dict[inv_type][rep_type][rep_key].add(to_add)


def _split_formulas_to_dict(cr, formulas):
    result = {}
    for f in formulas.split(";"):
        [column, formula] = f.split("=")
        column = column.strip()
        result.update({column: formula})
    return result


def _get_tax_group_percent(cr, tax_group):
    sum_plus = 0
    sum_minus = 0
    for child in tax_group.children_tax_ids:
        if child.amount < 0:
            sum_minus += child.amount
        else:
            sum_plus += child.amount
    return max(abs(sum_minus), sum_plus)
