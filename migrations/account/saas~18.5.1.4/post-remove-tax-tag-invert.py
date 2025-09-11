from itertools import groupby

from odoo.upgrade import util

account = util.import_script("account/saas~18.5.1.4/pre-remove-tax-tag-invert.py")


def migrate(cr, version):
    env = util.env(cr)

    cr.execute("""
        SELECT company_id, date, account_id, tag_id, balance
          FROM _upg_to_create_aml
      ORDER BY company_id, date, account_id
    """)
    lines_to_create = cr.fetchall()
    if lines_to_create:
        # Recreate errors from the past in order to have the same tax report before/after
        # There should hopefully not be too many cases
        journals = env["account.journal"].create(
            [
                {
                    "name": "Tax Tag Upgrade",
                    "code": "UPGTAG",
                    "type": "general",
                    "company_id": cid,
                }
                for cid in {cid for cid, *_ in lines_to_create}
            ]
        )
        company_id2journal = journals.grouped(lambda journal: journal.company_id.id)
        create_vals = []
        for (company_id, date), company_line_vals in groupby(lines_to_create, lambda row: row[0:2]):
            for account_id, account_line_vals in groupby(company_line_vals, lambda row: row[2]):
                line_vals = list(account_line_vals)  # materialize the generator to iterate multiple times
                create_vals.append(
                    {
                        "date": date,
                        "journal_id": company_id2journal[company_id].id,
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "balance": -2 * balance,
                                    "account_id": account_id,
                                    "tax_tag_ids": [(6, 0, [tag_id])],
                                },
                            )
                            for (*_, tag_id, balance) in line_vals
                        ]
                        + [
                            (
                                0,
                                0,
                                {
                                    "balance": 2 * sum(balance for (*_, balance) in line_vals),
                                    "account_id": account_id,
                                },
                            ),
                        ],
                    }
                )
        util.iter_browse(env["account.move"], []).create(create_vals).action_post()
        journals.active = False
        util.add_to_migration_reports(
            "Some taxes were badly configured. Corrections have been done in the journal UPGTAG in order to keep the same report values."
            "Accounting",
        )

    account.update_m2m_tag_rel(cr, "account_account_tag_account_tax_repartition_line_rel")
    account.update_m2m_tag_rel(cr, "account_account_tag_account_move_line_rel")
    cr.execute(
        """
              WITH updating_name AS (
                       UPDATE account_account_tag tag
                          SET name = name || jsonb_build_object('en_US', SUBSTRING(tag.name->>'en_US' FROM 2))
                         FROM _upg_tag_pairs
                        WHERE tag.id = _upg_tag_pairs.plus_tag_id
                   )
       DELETE FROM account_account_tag tag
             WHERE tag.id IN (SELECT minus_tag_id FROM _upg_tag_pairs)
        """
    )
