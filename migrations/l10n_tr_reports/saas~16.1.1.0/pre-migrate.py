from odoo.upgrade import util

M = "l10n_tr_reports"


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, f"{M}.account_financial_report_l10n_tr_bilanco", f"{M}.account_report_l10n_tr_balance_sheet")
    util.rename_xmlid(
        cr, f"{M}.account_financial_report_l10n_tr_bilanco_column", f"{M}.account_report_l10n_tr_balance_sheet_column"
    )

    trbs = """
        active
        1
        10 100 101 102 103 108
        11 110 111 112 118 119
        12 120 121 122 126 127 128 129
        13 131 132 133 135 136 137 138 139
        15 150 151 152 153 157 158 159
        17 170 179
        18 180 181
        19 190 191 192 193 195 196 197 198 199
        2
        22 220 221 222 226 229
        23 231 232 233 235 236 237 239
        24 240 241 242 243 244 245 246 247 248 249
        25 250 251 252 253 254 255 256 257 258 259
        26 260 261 262 263 264 267 268 269
        27 271 272 277 278 279
        28 280 281
        29 291 292 293 294 295 297 298 299

        pasive
        3
        30 300 303 304 305 306 308 309
        32 320 321 322 326 329
        33 331 332 333 335 336 337
        34 340 349
        35 350
        36 360 361 368 369
        37 370 371 372 373 379
        38 380 381
        39 391 392 393 397 399
        4
        40 400 405 407 408 409
        42 420 421 422 426 429
        43 431 432 433 436 437 438
        44 440 449
        47 472 479
        48 480 481
        49 492 493 499
        5
        50 500 501
        52 520 521 522 523 529
        54 540 541 542 548 549
        57 570
        58 58_balance 580
        59 590 591
    """

    for suffix in trbs.split():
        util.rename_xmlid(cr, *eb(M + ".account_{financial_,}report_line_trbs_" + suffix))

    rm = """
        103 119 122 129 137 139 158 199
        222 229 237 239 241 243 244 246 247 249 257 268 278 298 299
        309 322 337
        408 422 437
        501 591
    """
    for infix in rm.split():
        util.remove_record(cr, f"{M}.account_financial_report_line_trbs_{infix}_balance")

    rm_line_balance_imd = tuple(f"account_report_line_trbs_{infix}" for infix in ["570", "580", "590"])
    cr.execute(
        """
        DELETE FROM account_report_expression e
         USING ir_model_data d
         WHERE d.module = %s
           AND d.res_id = e.report_line_id
           AND d.name IN %s
           AND e.label = 'balance'
        """,
        [
            M,
            rm_line_balance_imd,
        ],
    )
