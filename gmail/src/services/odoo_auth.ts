import { HOST, ODOO_AUTH_URLS } from "../consts";
import { User } from "../models/user";
import { encodeQueryData, postJsonRpc } from "../utils/http";
import { ERROR_PAGE, RAINBOW } from "./pages";

/**
 * Callback function called during the OAuth authentication process.
 *
 * 1. The user click on the "Login button"
 *    We generate a state token (for this function)
 * 2. The user is redirected to Odoo and enter his login / password
 * 3. Then the user is redirected to the Google App-Script
 * 4. Thanks the state token, the function "odooAuthCallback" is called with the auth code
 * 5. The auth code is exchanged for an access token with a RPC call
 */
export async function odooAuthCallback(callbackRequest: any) {
    const { success, auth_code: authCode, state } = callbackRequest.query;
    if (success !== "1") {
        return ERROR_PAGE.replace("__ERROR_MESSAGE__", "Odoo did not return successfully.");
    }
    const { email, loginToken } = JSON.parse(state);
    let response = null;
    let user = null;
    try {
        user = await User.getUserFromLoginToken(email, loginToken);

        console.log("Get access token from auth code...");
        response = await postJsonRpc(user.odooUrl + ODOO_AUTH_URLS.CODE_VALIDATION, {
            auth_code: authCode,
        });
        if (!response || !response.access_token || !response.access_token.length) {
            throw new Error("Odoo exchange failed");
        }
    } catch {
        return ERROR_PAGE.replace(
            "__ERROR_MESSAGE__",
            "The token exchange failed. Maybe your token has expired or your database can not be reached by the Google server." +
                "<hr noshade>Contact your administrator or our support.",
        );
    }
    user.setOdooToken(response.access_token);
    return RAINBOW;
}

/**
 * Generate the URL to redirect the user for the authentication to the Odoo database.
 *
 * This URL contains a state and the Odoo database should resend it.
 * The Google server uses the state code to know which function to execute when the user
 * is redirected on their server.
 */
export async function getOdooAuthUrl(user: User): Promise<string> {
    const odooUrl = user.odooUrl;
    if (!odooUrl || !odooUrl.length) {
        throw new Error("Can not retrieve the Odoo database URL.");
    }

    const loginToken = await user.generateLoginToken();

    const redirectToAddon = `${HOST}/auth_callback`;

    return (
        odooUrl +
        ODOO_AUTH_URLS.AUTH_CODE +
        encodeQueryData({
            redirect: redirectToAddon,
            friendlyname: "Gmail",
            state: JSON.stringify({ loginToken, email: user.email }),
            scope: ODOO_AUTH_URLS.SCOPE,
        })
    );
}

/**
 * Make an HTTP request to the Odoo database to verify that the server
 * is reachable and that the mail plugin module is installed.
 *
 * Returns the version of the addin that is supported if it's reachable, null otherwise.
 */
export async function getSupportedAddinVersion(odooUrl: string): Promise<number | null> {
    if (!odooUrl?.length) {
        return null;
    }
    const response = await postJsonRpc(odooUrl + ODOO_AUTH_URLS.CHECK_VERSION);
    return response ? parseInt(response) : null;
}
