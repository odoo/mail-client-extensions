# -*- coding: utf-8 -*-
import itertools
import logging
import re

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.account.saas-13.2." + __name__)


def migrate(cr, version):
    # ===========================================================
    # Sequence Performances (PR:53393)
    # ===========================================================
    util.create_column(cr, "account_journal", "sequence_override_regex", "varchar")
    for table in ["account_move", "account_bank_statement"]:
        util.create_column(cr, table, "sequence_prefix", "varchar")
        util.create_column(cr, table, "sequence_number", "int4")

    class Substitue:
        def __init__(self, placeholder, match, group):
            self.placeholder = f"%({placeholder})s"
            self.regex = rf"(?P<{group}>({match})?)" if group else rf"(?:{match})?"
            self.deprecated = not group

        @classmethod
        def make(cls, placeholder, match, group):
            return [
                cls(placeholder, match, group),
                cls(f"range_{placeholder}", match, group),
                cls(f"current_{placeholder}", match, group),
            ]

    substitutes = list(
        itertools.chain.from_iterable(
            [
                Substitue.make("year", r"\d{4}", "year"),
                Substitue.make("month", r"\d{2}", "month"),
                Substitue.make("y", r"\d{2}", "year"),
                Substitue.make("day", r"\d{2}", None),
                Substitue.make("doy", r"\d{3}", None),
                Substitue.make("woy", r"\d{2}", None),
                Substitue.make("weekday", r"\d", None),
                Substitue.make("h24", r"\d{2}", None),
                Substitue.make("h12", r"\d{2}", None),
                Substitue.make("min", r"\d{2}", None),
                Substitue.make("sec", r"\d{2}", None),
            ]
        )
    )
    deprecated_placeholders = {s.placeholder for s in substitutes if s.deprecated}
    bad_journals = []

    cr.execute(
        """
            SELECT j.id,
                   j.name,
                   j.active,
                   COALESCE(s.prefix, '') AS prefix,
                   COALESCE(s.suffix, '') AS suffix
              FROM account_journal j
              JOIN ir_sequence s ON j.sequence_id = s.id
        """
    )

    for jid, name, active, prefix, suffix in cr.fetchall():
        if active:
            deactivate = False
            if re.search(r"%\(\w+\)s", prefix) and re.search(r"%\(\w+\)s", suffix):
                deactivate = True
                msg = f"The journal {name} (id={jid}) use placeholders in both prefix and suffix. This is not supported anymore."
                _logger.error(msg)
                bad_journals.append(msg)

            xfix = prefix + suffix
            deprec = ",".join(p for p in deprecated_placeholders if p in xfix)
            if deprec:
                deactivate = True
                msg = f"The journal {name} (id={jid}) use deprecated placeholder(s) ({deprec}) that are not supported anymore."
                _logger.error(msg)
                bad_journals.append(msg)

            if deactivate:
                cr.execute("UPDATE account_journal SET active = false WHERE id = %s", [jid])

        if suffix and re.search(r"(\d|%\(\w+\)s)", suffix):
            grouped = "|".join(re.escape(sub.placeholder) for sub in substitutes)
            suffix_regex = (
                "".join(
                    r"(?P<suffix{}>\D*?){}".format(i, sub.regex)
                    for i, m in enumerate(re.finditer(grouped, suffix), 1)
                    for sub in substitutes
                    if sub.placeholder in m.group(0)  # there should be only one match among all substitutes
                )
                + r"(?P<suffix>\D*?)"
            )
            regex = rf"^(?P<prefix1>.*?)(?P<seq>\d*){suffix_regex}$"
            cr.execute("UPDATE account_journal SET sequence_override_regex = %s WHERE id = %s", [regex, jid])

            number = re.sub(r"\?P<\w+>", "?:", regex.replace(r"?P<seq>", ""))
            prefix = re.sub(r"\?P<\w+>", "", re.sub(r"(\?<seq>.*)", "(?:.*)", regex))
            for table in ["account_move", "account_bank_statement"]:
                cr.execute(
                    f"""
                        UPDATE {table}
                           SET sequence_prefix = (regexp_match(name, %s))[1],
                               sequence_number = ('0' || (regexp_match(name, %s))[1])::integer
                         WHERE journal_id = %s;
                    """,
                    [prefix, number, jid],
                )

    if bad_journals:
        util.add_to_migration_reports(
            """<details>
                 <summary>Some account journals has been deactivated</summary>
                 <ul>{}</ul>
               </details>
            """.format(
                "".join(f"<li>{util.html_escape(b)}</li>" for b in bad_journals)
            ),
            format="html",
            category="Accounting",
        )

    # default match
    for table in ["account_move", "account_bank_statement"]:
        query = (
            r"""
                UPDATE %s
                   SET sequence_prefix = (regexp_match(name, '^(.*?)(?:\d{{0,9}})(?:\D*?)$'))[1],
                       sequence_number = ('0' || (regexp_match(name, '^(?:.*?)(\d{{0,9}})(?:\D*?)$'))[1])::integer
                 WHERE sequence_number IS NULL
            """
            % table
        )
        util.parallel_execute(cr, util.explode_query_range(cr, query, table))

    # ===
    util.remove_field(cr, "account.journal", "sequence_id")
    util.remove_field(cr, "account.journal", "refund_sequence_id")
    util.remove_field(cr, "account.journal", "sequence_number_next")
    util.remove_field(cr, "account.journal", "refund_sequence_number_next")

    util.create_column(cr, "account_journal", "sale_activity_type_id", "int4")
    util.create_column(cr, "account_journal", "sale_activity_user_id", "int4")
    util.create_column(cr, "account_journal", "sale_activity_note", "text")

    util.create_column(cr, "account_move", "posted_before", "boolean")
    util.explode_execute(
        cr,
        "UPDATE account_move SET posted_before = (state = 'posted' OR name != '/')",
        table="account_move",
    )

    util.rename_field(cr, "account.move", "invoice_payment_state", "payment_state")
    util.remove_field(cr, "account.move", "invoice_partner_icon")
    util.remove_field(cr, "account.move", "invoice_sequence_number_next")
    util.remove_field(cr, "account.move", "invoice_sequence_number_next_prefix")

    util.create_column(cr, "account_move_line", "matching_number", "varchar")
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line l
           SET matching_number = f.name
          FROM account_full_reconcile f
         WHERE f.id = l.full_reconcile_id
           AND l.matching_number IS NULL
        """,
        table="account_move_line",
        alias="l",
    )
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line l
           SET matching_number = 'P'
          FROM account_partial_reconcile p
         WHERE (p.credit_move_id = l.id OR p.debit_move_id = l.id)
           AND l.matching_number IS NULL
        """,
        table="account_move_line",
        alias="l",
    )

    util.create_column(cr, "res_company", "account_opening_date", "date")
    cr.execute(
        """
        UPDATE res_company c
           SET account_opening_date = m.date
          FROM account_move m
         WHERE m.id = c.account_opening_move_id
    """
    )

    util.rename_field(cr, "account.invoice.report", "invoice_payment_state", "payment_state")

    util.add_to_migration_reports(
        """
        <p><strong>IMPORTANT NOTICE</strong></p>
        <p>
            The numbering of journal entries & invoices changed in Odoo 14;
            sequences are replaced by a more robust approach, to prevent mistakes
            (e.g. 2020/12/0003 for an invoice posted in *September*, or  2020/00003 for a document in fiscal year 2019).
        </p>
        <p>
            If you had wrong journal entries,
            you might face <a href="https://i.imgur.com/7wQW1vT.png" target="_blank">blocking messages like this</a>
            when validating a document.
            To fix such issues, you can either correct the number of the last journal entry for the month / year, or
            assign a number manually on a draft document before posting it.
            To do so, use the "Renumbering" action available from the *list* of journal entries.
            Once you fix the latest entry, all future entries will be correct.
        </p>
        """,
        "Accounting",
        format="html",
    )
