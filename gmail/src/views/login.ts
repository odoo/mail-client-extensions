import { State } from "../models/state";
import { User } from "../models/user";
import { getOdooAuthUrl, getSupportedAddinVersion } from "../services/odoo_auth";
import {
    ActionCall,
    EventResponse,
    Notify,
    OpenLink,
    OpenLinkOpenAs,
    Redirect,
    registerEventHandler,
} from "../utils/actions";
import { Card, CardSection, Image, TextInput } from "../utils/components";
import { formatUrl } from "../utils/format";

/**
 * Initiate the authentication process, and redirect to the Odoo database.
 */
async function onNextLogin(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    let domain = null;
    try {
        domain = new URL(formatUrl(formInputs.odooServerUrl)).origin;
    } catch {}
    if (!domain) {
        return new Notify(`Invalid URL ${formInputs.odooServerUrl}`);
    }

    user.odooUrl = domain
    await user.save();

    const version = await getSupportedAddinVersion(domain);
    if (!version) {
        return new Notify("Could not connect to your database.");
    }

    if (version !== 2) {
        return new Notify(
            "This addin version required Odoo 19.2 or a newer version, please install an older addin version.",
        );
    }
    const odooLoginUrl = await getOdooAuthUrl(user);
    return new Redirect(new OpenLink(odooLoginUrl, OpenLinkOpenAs.OVERLAY, true));
}
registerEventHandler(onNextLogin);

export async function getLoginMainView(user: User) {
    return new Card([
        new CardSection([
            new Image("/assets/login_header.svg.png", "Connect to your Odoo database"),
            new TextInput(
                "odooServerUrl",
                "Connect to...",
                new ActionCall(undefined, onNextLogin),
                "e.g. company.odoo.com",
                user.odooUrl,
            ),
            new Image(
                "/render_button/875a7b/ffffff/Login",
                "Login",
                new ActionCall(undefined, onNextLogin),
            ),
            new Image(
                "/render_button/e7e9ed/1e1e1e/Sign%20Up",
                "Sign Up",
                new OpenLink(
                    "https://www.odoo.com/trial?selected_app=mail_plugin:crm:helpdesk:project",
                ),
            ),
            new Image(
                "/render_button/ffffff/2f9e44/FAQ",
                "FAQ",
                new OpenLink(
                    "https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html",
                ),
            ),
        ]),
    ]);
}
