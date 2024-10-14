# ruff: noqa: ERA001, PLW2901
import ast
import lib2to3.pgen2.driver
import logging
import re
from lib2to3.pgen2.parse import ParseError
from lib2to3.refactor import RefactoringTool, get_all_fix_names

lib2to3_logger = logging.getLogger("lib2to3.driver")


class Lib2to3LoggingShim(object):
    def getLogger(self):
        return logging.getLogger("lib2to3.driver")


lib2to3.pgen2.driver.logging = Lib2to3LoggingShim()

logging.getLogger("lib2to3.driver").setLevel(logging.WARNING)
logging.getLogger("RefactoringTool").setLevel(logging.WARNING)
_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base.saas-17." + __name__)

from odoo.addons.base.maintenance.migrations import util  # noqa: E402

PKG = "lib2to3.fixes"


def migrate(cr, version):
    # ensure views have no xml declaration with encoding
    cr.execute(r"""
        UPDATE ir_ui_view
           SET arch_db = regexp_replace(arch_db, '^<\?xml[^>]+encoding=[^>]+\?>', '<?xml version="1.0"?>')
         WHERE arch_db ~ '^<\?xml[^>]+encoding=[^>]+\?>'
    """)

    all_fixes = [f"{PKG}.fix_{f}" for f in get_all_fix_names(PKG)]
    # inline_fixes = [
    #     'basestring', 'dict', 'filter', 'has_key', 'idoms', 'isinstance', 'long', 'map', 'ne',
    #     'numliterals', 'paren', 'set_literal', 'unicode', 'ws_comma', 'zip'
    # ]
    rt = RefactoringTool(all_fixes)

    columns = util.splitlines("""
        ir_act_server.code
        ir_server_object_line.value
        ir_act_report_xml.attachment
        ir_act_report_xml.print_report_name

        ir_model_fields.compute

        account_tax.python_compute
        account_tax.python_applicable
        gamification_goal_definition.compute_code
        hr_salary_rule.condition_python
        hr_salary_rule.amount_python_compute

        marketing_campaign_activity.condition

        # enterprise
        account_financial_html_report_line.formulas
    """)
    for tc in columns:
        table, _, column = tc.rpartition(".")
        if not util.column_exists(cr, table, column):
            continue
        cr.execute(
            """
            SELECT id, {column}
              FROM {table}
             WHERE {column} IS NOT NULL
        """.format(column=column, table=table)
        )
        for rid, value in cr.fetchall():
            try:
                ast.parse(value, "", "exec")
            except TabError:
                # python3 is pickier than python2 regarding mixture of spaces and tabs.
                value = re.sub("\t", 8 * " ", value)
            except Exception:
                pass  # let `refactor_string` fail and report the error
            strip = None
            if not value.endswith("\n"):
                # lib2to3 parser WANT a trailing carriage return.
                value += "\n"
                strip = -1  # will remove last character
            try:
                refactored = str(rt.refactor_string(util.dedent(value), "%s,%d" % (tc, rid)))[:strip]
            except (ParseError, IndentationError):
                model = util.model_of_table(cr, table).title().replace(".", "")
                _logger.warning("Cannot refactor %s(%d).%s", model, rid, column)
                continue
            if value != refactored:
                cr.execute(
                    """
                    UPDATE {table}
                       SET {column} = %s
                     WHERE id = %s
                """.format(column=column, table=table),
                    [refactored, rid],
                )

    # easy replacements (only `L` numeric suffix)
    columns = util.splitlines("""
        ir_filters.domain
        ir_filters.context
        ir_act_window.domain
        ir_act_window.context

        ir_model_fields.selection
        ir_model_fields.domain

        ir_rule.domain_force

        res_lang.grouping       # who's stupid change this?

        base_automation.filter_pre_domain
        base_automation.filter_domain
        base_action_rule.filter_pre_domain      # < saas~14 compatibility, (not yet renamed)
        base_action_rule.filter_domain          # ditto

        base_partner_merge_line.aggr_ids

        pos_cache.product_domain

        gamification_challenge.user_domain
        gamification_goal_definition.domain
        gamification_goal_definition.batch_user_expression

        hr_salary_rule.condition_range
        hr_salary_rule.quantity
        hr_salary_rule.amount_percentage_base

        mail_alias.alias_defaults
        mail_mail.headers           # should already be safe. just in case
        mail_compose_message.active_domain

        mail_mass_mailing.mailing_domain

        # enterprise
        account_financial_html_report_line.domain
        sale_coupon_rule.rule_partners_domain
        sale_coupon_rule.rule_products_domain
        sale_coupon_generate.partners_domain
        team_user.team_user_domain
        crm_team.score_team_domain
        website_crm_score.domain
    """)
    for tc in columns:
        table, _, column = tc.rpartition(".")
        if not util.column_exists(cr, table, column):
            continue
        cr.execute(
            r"""
            UPDATE {table}
               SET {column} = regexp_replace({column}, '\y(\d+)[Ll]\y', E'\\1', 'g')
             WHERE {column} ~ '\y\d+[Ll]\y'     -- avoid touching all rows
        """.format(table=table, column=column)
        )

    # special cases
    cr.execute("SELECT character_set_name FROM information_schema.character_sets")
    (charset,) = cr.fetchone()
    cr.execute(
        r"""
        UPDATE ir_act_client
           SET params_store = convert_to(regexp_replace(convert_from(params_store, '{0}'),
                                                        '\y(\d+)[Ll]\y', E'\1', 'g'),
                                         '{0}')
    """.format(charset)
    )

    cr.execute(r"""
        UPDATE ir_config_parameter
           SET value = regexp_replace(value, '\y(\d+)[Ll]\y', E'\\1', 'g')
         WHERE key IN ('auth_signup.template_user_id', 'default_sms_provider_id')
    """)
