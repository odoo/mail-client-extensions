import express from "express";
import asyncHandler from "express-async-handler";
import fs from "fs/promises";
import { google } from "googleapis";
import jwt from "jsonwebtoken";
import cron from "node-cron";
import path from "path";
import { Email } from "./models/email";
import { Partner } from "./models/partner";
import { State } from "./models/state";
import { User } from "./models/user";
import { odooAuthCallback } from "./services/odoo_auth";
import { Translate } from "./services/translation";
import { getEventHandler } from "./utils/actions";
import pool from "./utils/db";
import { htmlEscape } from "./utils/format";
import { svgToPngResponse } from "./utils/svg";
import { getLoginMainView } from "./views/login";
import { getPartnerView } from "./views/partner";
import { getSearchPartnerView } from "./views/search_partner";

const gmail = google.gmail({ version: "v1" });

const app = express();
app.use(express.json());

// Load the application secret from `.env`
require("dotenv").config({ quiet: true });
if (!process.env.APP_SECRET?.length) {
    throw new Error("Application secret not configured");
}

/**
 * Once a day, clean the old email log table.
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
        const [user, headers] = await Promise.all([
            User.getUserFromGoogleToken(req.body),
            Email.getEmailHeadersFromGoogleToken(req.body),
        ]);

        if (!user.odooUrl?.length || !user.odooToken?.length) {
            res.json((await getLoginMainView(user)).build());
            return;
        }

        const email = await Email.getEmailFromHeaders(req.body, headers, user);

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
        const decoded = jwt.verify(parameters.token, process.env.APP_SECRET, {
            algorithms: ["HS256"],
        });

        const functionName = decoded.functionName;
        const state = decoded.state && State.fromJson(decoded.state);
        const args = decoded.arguments || {};

        if (state?.email) {
            // Update the Gmail tokens
            state.email.userOAuthToken = req.body.authorizationEventObject.userOAuthToken;
            state.email.accessToken = req.body.gmail.accessToken;
        }

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

/**
 * Serve the SVG files as PNG, because Google won't fetch SVG.
 */
app.use("/assets", async (req, res, next) => {
    if (!req.path.endsWith(".svg.png")) {
        return next();
    }

    const filename = req.path.slice(1, -4);

    // Prevent directory traversal
    if (!/^[a-z0-9_-]+\.svg$/.test(filename)) {
        res.sendStatus(404);
        return;
    }
    const base = path.join(__dirname, "assets");
    const fullPath = path.resolve(path.join(base, filename));
    if (!fullPath.startsWith(`${base}/`)) {
        res.sendStatus(404);
        return;
    }

    try {
        svgToPngResponse(await fs.readFile(fullPath), res);
    } catch (err) {
        res.sendStatus(404);
    }
});

/**
 * For some views, we want button that takes the full width of the card,
 * this is not possible with standard button widget, and so we use SVG
 * file with a link.
 */
app.use("/render_button/:backgroundColor/:textColor/:label", async (req, res, next) => {
    const { backgroundColor, textColor, label } = req.params;
    if (!/^[0-9a-z]{6}$/.test(backgroundColor) || !/^[0-9a-z]{6}$/.test(textColor)) {
        console.error("Invalid color code", req.params)
        res.sendStatus(404);
        return;
    }

    const svg = await fs.readFile(path.join(__dirname, "assets/button.svg"));
    const svgText = svg
        .toString()
        .replace("__TEXT__", htmlEscape(label))
        .replace("__STROKE__", `#${backgroundColor}`)
        .replace("__FILL__", `#${backgroundColor}`)
        .replace("__COLOR__", `#${textColor}`);
    try {
        svgToPngResponse(Buffer.from(svgText), res);
    } catch (err) {
        console.error("Failed to generate the button", err)
        res.sendStatus(404);
    }
});

/**
 * Render the "No result" SVG, with the translated text in it.
 */
app.use("/render_search_no_result/:title/:subtitle", async (req, res, next) => {
    const { title, subtitle } = req.params;

    const svg = await fs.readFile(path.join(__dirname, "assets/search_no_result.svg"));
    const svgText = svg
        .toString()
        .replace("No record found.", htmlEscape(title))
        .replace("Try using different keywords.", htmlEscape(subtitle));
    try {
        svgToPngResponse(Buffer.from(svgText), res);
    } catch (err) {
        res.sendStatus(404);
    }
});

app.use(
    "/assets",
    express.static(path.join(__dirname, "assets"), {
        fallthrough: false,
        immutable: true,
        maxAge: "1y",
    }),
);

const server = app.listen(5000, () => {
    const address = server.address();
    if (typeof address === "object" && address?.port) {
        console.log("Running on port", address.port);
    }
});
