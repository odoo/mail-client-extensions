# -*- coding: utf-8 -*-
# ruff: noqa: UP031
import logging

from odoo import modules

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.account.0.0.0."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    if not util.version_gte("saas~16.2"):
        _fix_tags(cr)


def _fix_tags(cr):
    pre_config = util.ENVIRON["account_tags_pre_config"]

    cr.execute(
        """
              SELECT at.account_account_tag_id, company.id, ARRAY_AGG(account.code)
                FROM account_account_template_account_tag at
                JOIN account_account_template account ON at.account_account_template_id = account.id
                JOIN res_company company ON company.chart_template_id = account.chart_template_id
            GROUP BY at.account_account_tag_id, company.id
            ORDER BY at.account_account_tag_id
        """
    )

    post_config = cr.fetchall()

    pre_config = {tuple(c[:2]): c[2] for c in pre_config}
    post_config = {tuple(c[:2]): c[2] for c in post_config}

    add_tags = {}
    remove_tags = {}

    for tag_chart in list(pre_config.keys()) + list(post_config.keys()):
        add_tags[tag_chart] = set(post_config.get(tag_chart, [])) - set(pre_config.get(tag_chart, []))
        remove_tags[tag_chart] = set(pre_config.get(tag_chart, [])) - set(post_config.get(tag_chart, []))

    tags_charts = list(add_tags.keys()) + list(remove_tags.keys())
    if tags_charts:
        standard_modules = list(modules.get_modules())
        cr.execute(
            util.format_query(
                cr,
                """
                   SELECT tag.id, tag.{}, md.module || '.' || md.name
                     FROM account_account_tag tag
                LEFT JOIN ir_model_data md ON (md.model = 'account.account.tag' AND md.res_id = tag.id)
                    WHERE tag.id in %s
                """,
                util.get_value_or_en_translation(cr, "account_account_tag", "name"),
            ),
            (tuple(t[0] for t in tags_charts),),
        )

        tags = {tag[0]: {"name": tag[1], "xmlid": tag[2]} for tag in cr.fetchall()}

        for (tag_id, company_id), codes in add_tags.items():
            added_accounts = []
            for code in codes:
                cr.execute(
                    """
                           INSERT INTO account_account_account_tag(account_account_id, account_account_tag_id)
                                SELECT a.id, %s
                                  FROM account_account a
                                 WHERE a.company_id = %s AND a.code LIKE %s
                        ON CONFLICT DO NOTHING
                             RETURNING account_account_id
                    """,
                    (tag_id, company_id, code.replace("_", r"\_") + "%"),
                )
                added_accounts += [r[0] for r in cr.fetchall()]

            if added_accounts:
                cr.execute("SELECT code, id FROM account_account WHERE id in %s", (tuple(added_accounts),))
                added_accounts = ", ".join("%s(#%s)" % account for account in cr.fetchall())
                _logger.info(
                    "Added tag %s(#%s) on accounts %s",
                    tags[tag_id]["xmlid"] or tags[tag_id]["name"],
                    tag_id,
                    added_accounts,
                )
                util.add_to_migration_reports(
                    "The tag %s has been added to the accounts %s" % (tags[tag_id]["name"], added_accounts),
                    "Accounting",
                )

        for (tag_id, company_id), codes in remove_tags.items():
            if (
                tag_id not in tags
                or not tags[tag_id]["xmlid"]
                or tags[tag_id]["xmlid"].split(".")[0] not in standard_modules
            ):
                # Do not remove custom tags from the accounts
                # They could have been deleted from the templates because of a `[(6,)]` command
                # in the standard module of the l10n module, but they should actually remain because
                # the custom module adds them back with a `[(4,)]` command afterwards.
                continue
            removed_accounts = []
            for code in codes:
                cr.execute(
                    """
                        DELETE FROM account_account_account_tag
                              WHERE account_account_tag_id = %s
                                AND account_account_id in (
                                    SELECT a.id
                                      FROM account_account a
                                     WHERE a.company_id = %s AND a.code LIKE %s)
                          RETURNING account_account_id
                    """,
                    (tag_id, company_id, code.replace("_", r"\_") + "%"),
                )
                removed_accounts += [r[0] for r in cr.fetchall()]

            if removed_accounts:
                cr.execute("SELECT code, id FROM account_account WHERE id in %s", (tuple(removed_accounts),))
                removed_accounts = ", ".join("%s(#%s)" % account for account in cr.fetchall())
                _logger.info(
                    "Removed tag %s(#%s) on accounts %s",
                    tags[tag_id]["xmlid"] or tags[tag_id]["name"],
                    tag_id,
                    removed_accounts,
                )
                util.add_to_migration_reports(
                    "The tag %s has been removed from the accounts %s" % (tags[tag_id]["name"], removed_accounts),
                    "Accounting",
                )
