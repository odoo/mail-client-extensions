import { ODOO_AUTH_URLS } from "../const";
import { postJsonRpc, encodeQueryData } from "../utils/http";

const errorPage = `
<html>
    <style>
        .alert {
            color: #721c24;
            background-color: #f5c6cb;
            padding: 20px;
            max-width: 1000px;
            margin: auto;
            text-align: center;
            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"
        }
        img {
            max-width: 300px;
            margin-left: calc(50% - 150px);
            margin-bottom: 50px;
        }
        hr {
            border- color: #721c24;
        }
    </style>
    <img src="https://raw.githubusercontent.com/odoo/mail-client-extensions/master/outlook/assets/odoo-full.png">
    <div class="alert">__ERROR_MESSAGE__</div>
</html>`;

/**
 * Callback function called during the OAuth authentication process.
 *
 * 1. The user click on the "Login button"
 *    We generate a state token (for this function)
 * 2. The user is redirected to Odoo and enter his login / password
 * 3. Then the user is redirected to the Google App-Script
 * 4. Thanks the the state token, the function "odooAuthCallback" is called with the auth code
 * 5. The auth code is exchanged for an access token with a RPC call
 */
function odooAuthCallback(callbackRequest: any) {
    Logger.log("Run authcallback");
    const success = callbackRequest.parameter.success;
    const authCode = callbackRequest.parameter.auth_code;

    if (success !== "1") {
        return HtmlService.createHtmlOutput(
            errorPage.replace("__ERROR_MESSAGE__", "Odoo did not return successfully."),
        );
    }

    Logger.log("Get access token from auth code...");

    const userProperties = PropertiesService.getUserProperties();
    const odooUrl = userProperties.getProperty("ODOO_SERVER_URL");

    const response = postJsonRpc(odooUrl + ODOO_AUTH_URLS.CODE_VALIDATION, {
        auth_code: authCode,
    });

    if (!response || !response.access_token || !response.access_token.length) {
        return HtmlService.createHtmlOutput(
            errorPage.replace(
                "__ERROR_MESSAGE__",
                "The token exchange failed. Maybe your token has expired or your database can not be reached by the Google server." +
                    "<hr noshade>Contact your administrator or our support.",
            ),
        );
    }

    const accessToken = response.access_token;

    userProperties.setProperty("ODOO_ACCESS_TOKEN", accessToken);

    return HtmlService.createHtmlOutput("Success !");
}

/**
 * Generate the URL to redirect the user for the authentication to the Odoo database.
 *
 * This URL contains a state and the Odoo database should resend it.
 * The Google server use the state code to know which function to execute when the user
 * is redirected on their server.
 */
export function getOdooAuthUrl() {
    const userProperties = PropertiesService.getUserProperties();
    const odooUrl = userProperties.getProperty("ODOO_SERVER_URL");
    const scriptId = ScriptApp.getScriptId();

    if (!odooUrl || !odooUrl.length) {
        throw new Error("Can not retrieve the Odoo database URL.");
    }

    if (!scriptId || !scriptId.length) {
        throw new Error("Can not retrieve the script ID.");
    }

    const stateToken = ScriptApp.newStateToken().withMethod(odooAuthCallback.name).withTimeout(3600).createToken();

    const redirectToAddon = `https://script.google.com/macros/d/${scriptId}/usercallback`;
    const scope = ODOO_AUTH_URLS.SCOPE;

    const url =
        odooUrl +
        ODOO_AUTH_URLS.AUTH_CODE +
        encodeQueryData({
            redirect: redirectToAddon,
            friendlyname: "Gmail",
            state: stateToken,
            scope: scope,
        });

    return url;
}

/**
 * Return the access token saved in the user properties.
 */
export const getAccessToken = () => {
    const userProperties = PropertiesService.getUserProperties();
    const accessToken = userProperties.getProperty("ODOO_ACCESS_TOKEN");
    if (!accessToken || !accessToken.length) {
        return;
    }
    return accessToken;
};

/**
 * Reset the access token saved in the user properties.
 */
export const resetAccessToken = () => {
    const userProperties = PropertiesService.getUserProperties();
    userProperties.deleteProperty("ODOO_ACCESS_TOKEN");
};

/**
 * Make an HTTP request to the Odoo database to verify that the server
 * is reachable and that the mail plugin module is installed.
 *
 * Returns the version of the addin that is supported if it's reachable, null otherwise.
 */
export const getSupportedAddinVersion = (odooUrl: string): number | null => {
    if (!odooUrl || !odooUrl.length) {
        return null;
    }

    const response = postJsonRpc(odooUrl + ODOO_AUTH_URLS.CHECK_VERSION, {}, {}, { returnRawResponse: true });
    if (!response) {
        return null;
    }

    const responseCode = response.getResponseCode();

    if (responseCode > 299 || responseCode < 200) {
        return null;
    }

    const textResponse = response.getContentText("UTF-8");
    return parseInt(JSON.parse(textResponse).result);
};
