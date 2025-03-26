from odoo.upgrade import util


def update_phone_and_log(cr, model_name):
    """
    Updates the phone field with the mobile field for the specified table
    and logs the previous mobile number if applicable.
    """
    table_name = util.table_of_model(cr, model_name)
    query = util.format_query(
        cr,
        """
        WITH info AS (
            SELECT t.id,
                   t.phone,
                   t.mobile
              FROM {table_name} t
             WHERE t.mobile IS NOT NULL
               AND t.phone IS DISTINCT FROM t.mobile
               AND {{parallel_filter}}
        ), _upd AS (
            UPDATE {table_name}
               SET phone = info.mobile
              FROM info
             WHERE {table_name}.id = info.id
               AND info.phone IS NULL
         RETURNING {table_name}.id
        )
    """,
        table_name=table_name,
    )

    if util.module_installed(cr, "mail"):
        log_query = """
            INSERT INTO mail_message (
                        res_id, model, author_id, message_type,
                        body, date)
                 SELECT id, %s, %s, 'notification',
                        'Previous Mobile: ' || mobile, NOW() at time zone 'UTC'
                   FROM info
                  WHERE phone IS NOT NULL
        """
        query += cr.mogrify(log_query, [model_name, util.ref(cr, "base.partner_root")]).decode()
    elif table_name == "res_partner":
        comment_query = """
            UPDATE res_partner
               SET comment = COALESCE(comment, '') || '\nPrevious Mobile: ' || info.mobile
              FROM info
             WHERE res_partner.id = info.id
               AND info.phone IS NOT NULL
        """
        query += comment_query
    else:
        # Dummy query to ensure the CTEs are executed
        query += "SELECT 1 FROM _upd JOIN info ON _upd.id = info.id LIMIT 1"

    util.explode_execute(cr, query, table=table_name, alias="t")


def migrate(cr, version):
    old_xmlids = [
        "l10n_pl.state_pl_ds",
        "l10n_pl.state_pl_kp",
        "l10n_pl.state_pl_lb",
        "l10n_pl.state_pl_ls",
        "l10n_pl.state_pl_ld",
        "l10n_pl.state_pl_mp",
        "l10n_pl.state_pl_mz",
        "l10n_pl.state_pl_op",
        "l10n_pl.state_pl_pk",
        "l10n_pl.state_pl_pl",
        "l10n_pl.state_pl_pm",
        "l10n_pl.state_pl_sl",
        "l10n_pl.state_pl_sk",
        "l10n_pl.state_pl_wm",
        "l10n_pl.state_pl_wp",
        "l10n_pl.state_pl_zp",
        "l10n_pk.state_pk_ajk",
        "l10n_pk.state_pk_ba",
        "l10n_pk.state_pk_gb",
        "l10n_pk.state_pk_is",
        "l10n_pk.state_pk_kp",
        "l10n_pk.state_pk_pb",
        "l10n_pk.state_pk_sd",
        "l10n_iq.state_iq_01",
        "l10n_iq.state_iq_01_ar",
        "l10n_iq.state_iq_02",
        "l10n_iq.state_iq_02_ar",
        "l10n_iq.state_iq_03",
        "l10n_iq.state_iq_03_ar",
        "l10n_iq.state_iq_04",
        "l10n_iq.state_iq_04_ar",
        "l10n_iq.state_iq_05",
        "l10n_iq.state_iq_05_ar",
        "l10n_iq.state_iq_06",
        "l10n_iq.state_iq_06_ar",
        "l10n_iq.state_iq_07",
        "l10n_iq.state_iq_07_ar",
        "l10n_iq.state_iq_08",
        "l10n_iq.state_iq_08_ar",
        "l10n_iq.state_iq_09",
        "l10n_iq.state_iq_09_ar",
        "l10n_iq.state_iq_10",
        "l10n_iq.state_iq_10_ar",
        "l10n_iq.state_iq_11",
        "l10n_iq.state_iq_11_ar",
        "l10n_iq.state_iq_12",
        "l10n_iq.state_iq_12_ar",
        "l10n_iq.state_iq_13",
        "l10n_iq.state_iq_13_ar",
        "l10n_iq.state_iq_14",
        "l10n_iq.state_iq_14_ar",
        "l10n_iq.state_iq_15",
        "l10n_iq.state_iq_15_ar",
        "l10n_iq.state_iq_16",
        "l10n_iq.state_iq_16_ar",
        "l10n_iq.state_iq_17",
        "l10n_iq.state_iq_17_ar",
        "l10n_iq.state_iq_18",
        "l10n_iq.state_iq_18_ar",
        "l10n_bd.state_bd_a",
        "l10n_bd.state_bd_b",
        "l10n_bd.state_bd_c",
        "l10n_bd.state_bd_d",
        "l10n_bd.state_bd_e",
        "l10n_bd.state_bd_f",
        "l10n_bd.state_bd_g",
        "l10n_bd.state_bd_h",
        "l10n_at.state_at_1",
        "l10n_at.state_at_2",
        "l10n_at.state_at_3",
        "l10n_at.state_at_4",
        "l10n_at.state_at_5",
        "l10n_at.state_at_6",
        "l10n_at.state_at_7",
        "l10n_at.state_at_8",
        "l10n_at.state_at_9",
        "l10n_tw.state_tw_chh",
        "l10n_tw.state_tw_cic",
        "l10n_tw.state_tw_cih",
        "l10n_tw.state_tw_hch",
        "l10n_tw.state_tw_hct",
        "l10n_tw.state_tw_hlh",
        "l10n_tw.state_tw_ilh",
        "l10n_tw.state_tw_khc",
        "l10n_tw.state_tw_klc",
        "l10n_tw.state_tw_kmc",
        "l10n_tw.state_tw_lcc",
        "l10n_tw.state_tw_mlh",
        "l10n_tw.state_tw_ntc",
        "l10n_tw.state_tw_ntpc",
        "l10n_tw.state_tw_phc",
        "l10n_tw.state_tw_pth",
        "l10n_tw.state_tw_tcc",
        "l10n_tw.state_tw_tnh",
        "l10n_tw.state_tw_tpc",
        "l10n_tw.state_tw_tth",
        "l10n_tw.state_tw_tyc",
        "l10n_tw.state_tw_ylh",
    ]
    new_xmlids = [f"base.{xmlid.partition('.')[2]}" for xmlid in old_xmlids]

    for old, new in zip(old_xmlids, new_xmlids):
        util.rename_xmlid(cr, old, new, on_collision="merge")

    update_phone_and_log(cr, "res.partner")
    update_phone_and_log(cr, "res.company")

    util.remove_field(cr, "res.company", "mobile")
    util.remove_field(cr, "res.partner", "mobile")

    # Remove `--` in signature for following pattern(when it's at the start of the line):
    # `<p>--<br>Demo Signature 1</p>` to `<p>Demo Signature 1<p>`
    # `<div>-- <br>Demo Signature 2</div>` to `<div>Demo Signature 2</div>`
    # `<span>--<br>User</span>` to `<span>User</span>`
    sign_re = r"^((?:<[^>]*>)*)--\s*<br[^>]*>\s*"
    sign_query = cr.mogrify(
        r"""
        UPDATE res_users
           SET signature = REGEXP_REPLACE(ltrim(signature), %(re)s, '\1', 'm')
         WHERE ltrim(signature) ~ %(re)s
    """,
        {"re": sign_re},
    ).decode()
    util.explode_execute(cr, sign_query, table="res_users")
