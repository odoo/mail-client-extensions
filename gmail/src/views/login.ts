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
import { IMAGES_LOGIN } from "./icons";

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
    const loginButton = btoa(
        atob(IMAGES_LOGIN.buttonSVG)
            .replace("__TEXT__", "Login")
            .replace("__STROKE__", "#875a7b")
            .replace("__FILL__", "#875a7b")
            .replace("__COLOR__", "white"),
    );

    const signupButton = btoa(
        atob(IMAGES_LOGIN.buttonSVG)
            .replace("__TEXT__", "Sign Up")
            .replace("__STROKE__", "#e7e9ed")
            .replace("__FILL__", "#e7e9ed")
            .replace("__COLOR__", "#1e1e1e"),
    );

    const faqButton = btoa(
        atob(IMAGES_LOGIN.buttonSVG)
            .replace("__TEXT__", "FAQ")
            .replace("__STROKE__", "white")
            .replace("__FILL__", "white")
            .replace("__COLOR__", "#2f9e44"),
    );

    return new Card([
        new CardSection([
            new Image(IMAGES_LOGIN.loginSVG, "Connect to your Odoo database"),
            new TextInput(
                "odooServerUrl",
                "Connect to...",
                new ActionCall(undefined, onNextLogin),
                "e.g. company.odoo.com",
                user.odooUrl,
            ),
            new Image(
                "data:image/svg+xml;base64," + loginButton,
                "Login",
                new ActionCall(undefined, onNextLogin),
            ),
            new Image(
                "data:image/svg+xml;base64," + signupButton,
                "Sign Up",
                new OpenLink(
                    "https://www.odoo.com/trial?selected_app=mail_plugin:crm:helpdesk:project",
                ),
            ),
            new Image(
                "data:image/svg+xml;base64," + faqButton,
                "FAQ",
                new OpenLink(
                    "https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html",
                ),
            ),
        ]),
    ]);
}
