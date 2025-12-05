import express from "express";
import asyncHandler from "express-async-handler";
import { google } from "googleapis";
import cron from "node-cron";
import { getEventHandler } from "./utils/actions";

import { Email } from "./models/email";
import { Partner } from "./models/partner";
import { State } from "./models/state";
import { User } from "./models/user";
import { odooAuthCallback } from "./services/odoo_auth";
import { Translate } from "./services/translation";
import pool from "./utils/db";
import { getLoginMainView } from "./views/login";
import { getPartnerView } from "./views/partner";
import { getSearchPartnerView } from "./views/search_partner";

const gmail = google.gmail({ version: "v1" });

const app = express();
app.use(express.json());

/**
 * Once a day, clean the old email log row.
 */
cron.schedule("0 0 * * *", async () => {
    console.log("Clean the email logging table...");
    await pool.query(
        `
    DELETE FROM email_logs
          WHERE create_date < NOW() - INTERVAL '1 month'
        `,
    );
});

/**
 * Endpoint called the first time the user open an email, or when reloading.
 */
app.post(
    "/on_open_email",
    asyncHandler(async (req, res) => {
        const [user, eml] = await Promise.all([
            User.getUserFromGoogleToken(req.body),
            Email.getEmlFromGoogleToken(req.body),
        ]);

        if (!user.odooUrl?.length || !user.odooToken?.length) {
            res.json((await getLoginMainView(user)).build());
            return;
        }

        const email = await Email.getEmailFromEml(eml, user);

        if (email.contacts.length > 1) {
            // More than one contact, we will need to choose the right one
            const [_t, [searchedPartners, error]] = await Promise.all([
                Translate.getTranslations(user),
                Partner.searchPartner(
                    user,
                    email.contacts.map((c) => c.email),
                ),
            ]);

            if (error.code) {
                res.json((await getLoginMainView(user)).build());
                return;
            }
            const existingPartnersEmails = searchedPartners.map((p) => p.email);
            for (const contact of email.contacts) {
                if (existingPartnersEmails.includes(contact.email)) {
                    continue;
                }
                searchedPartners.push(
                    Partner.fromJson({ name: contact.name, email: contact.email }),
                );
            }

            const state = new State(null, false, email, searchedPartners, null, false);
            const searchPartnerView = await getSearchPartnerView(
                state,
                _t,
                user,
                "",
                false,
                _t("In this conversation"),
                true,
                true,
            );
            res.json(searchPartnerView.build());
            return;
        }

        // Only one partner, we can open the view immediately
        const [_t, [partner, canCreatePartner, canCreateProject, error]] = await Promise.all([
            Translate.getTranslations(user),
            Partner.getPartner(user, email.contacts[0].name, email.contacts[0].email),
        ]);

        if (error.code) {
            res.json((await getLoginMainView(user)).build());
            return;
        }

        const state = new State(partner, canCreatePartner, email, null, null, canCreateProject);

        res.json(getPartnerView(state, _t, user).build());
    }),
);

/**
 * Callback called by the addin when it executes an action.
 */
app.post(
    "/execute_action",
    asyncHandler(async (req, res) => {
        const user = await User.getUserFromGoogleToken(req.body);

        const _t = await Translate.getTranslations(user);

        const rawFormInputs = req.body.commonEventObject.formInputs || {};
        const formInputs = Object.fromEntries(
            Object.entries(rawFormInputs).map(([key, value]) => [
                key,
                value["stringInputs"]["value"][0],
            ]),
        );
        const parameters = req.body.commonEventObject.parameters;
        const functionName = parameters.functionName;
        const state = parameters.state && State.fromJson(parameters.state);
        const args = JSON.parse(parameters.arguments || "{}");

        const result = await getEventHandler(functionName)(state, _t, user, args, formInputs);
        res.json(result.build());
    }),
);

app.get(
    "/auth_callback",
    asyncHandler(async (req, res) => {
        res.send(await odooAuthCallback(req));
    }),
);

const server = app.listen(5000, () => {
    const address = server.address();
    if (typeof address === "object" && address?.port) {
        console.log("Running on port", address.port);
    }
});
