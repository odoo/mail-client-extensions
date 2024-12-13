from odoo.upgrade import util


def migrate(cr, version):
    if not util.column_exists(cr, "loyalty_card", "active"):
        util.create_column(cr, "loyalty_card", "active", "boolean", default=True)
    else:
        cr.execute("UPDATE loyalty_card SET active = true")

    # Merge points to one card if the program is Loyalty or e-Wallet and the partner has 2 cards as he should have
    # only one
    cr.execute(
        """
            WITH _dups AS (
                SELECT array_agg(card.id ORDER BY card.id DESC) AS id_list,
                       SUM(card.points) AS points
                  FROM loyalty_card card
                  JOIN loyalty_program program
                    ON card.program_id = program.id
                 WHERE program.applies_on = 'both'
                    OR (
                         program.program_type IN ('ewallet', 'loyalty')
                     AND program.applies_on = 'future'
                        )
              GROUP BY card.partner_id,
                       card.program_id
                HAVING count(*) > 1
            )
            UPDATE loyalty_card c
               SET points = CASE WHEN c.id = d.id_list[1] THEN d.points ELSE 0 END,
                   active = (c.id = d.id_list[1])
              FROM _dups d
             WHERE c.id = ANY(d.id_list)
        """
    )
