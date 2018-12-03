# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
   INSERT INTO account_cashbox_line(coin_value, number, default_pos_id)
        SELECT cl.coin_value, round(AVG(cl.number)), ps.config_id
          FROM account_cashbox_line cl
          JOIN account_bank_statement bs ON (bs.cashbox_start_id = cl.cashbox_id)
          JOIN pos_session ps ON (bs.pos_session_id = ps.id)
      GROUP BY cl.coin_value, ps.config_id
    """)
