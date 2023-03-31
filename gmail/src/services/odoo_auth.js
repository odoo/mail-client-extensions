var errorPage =
    '\n<html>\n    <style>\n        .alert {\n            color: #721c24;\n            background-color: #f5c6cb;\n            padding: 20px;\n            max-width: 1000px;\n            margin: auto;\n            text-align: center;\n            font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol"\n        }\n        img {\n            max-width: 300px;\n            margin-left: calc(50% - 150px);\n            margin-bottom: 50px;\n        }\n        hr {\n            border- color: #721c24;\n        }\n    </style>\n    <img src="https://raw.githubusercontent.com/odoo/mail-client-extensions/master/outlook/assets/odoo-full.png">\n    <div class="alert">__ERROR_MESSAGE__</div>\n</html>';
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
function odooAuthCallback(callbackRequest) {
    Logger.log("Run authcallback");
    var success = callbackRequest.parameter.success;
    var authCode = callbackRequest.parameter.auth_code;
    if (success !== "1") {
        return HtmlService.createHtmlOutput(
            errorPage.replace("__ERROR_MESSAGE__", "Odoo did not return successfully."),
        );
    }
    Logger.log("Get access token from auth code...");
    var userProperties = PropertiesService.getUserProperties();
    var odooUrl = userProperties.getProperty("ODOO_SERVER_URL");
    var response = (0, postJsonRpc)(odooUrl + ODOO_AUTH_URLS.CODE_VALIDATION, {
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
    var accessToken = response.access_token;
    userProperties.setProperty("ODOO_ACCESS_TOKEN", accessToken);
    return HtmlService.createHtmlOutput("Success ! <script>top.window.close()</script>");
}
/**
 * Generate the URL to redirect the user for the authentication to the Odoo database.
 *
 * This URL contains a state and the Odoo database should resend it.
 * The Google server use the state code to know which function to execute when the user
 * is redirected on their server.
 */
function getOdooAuthUrl() {
    var userProperties = PropertiesService.getUserProperties();
    var odooUrl = userProperties.getProperty("ODOO_SERVER_URL");
    var scriptId = ScriptApp.getScriptId();
    if (!odooUrl || !odooUrl.length) {
        throw new Error("Can not retrieve the Odoo database URL.");
    }
    if (!scriptId || !scriptId.length) {
        throw new Error("Can not retrieve the script ID.");
    }
    var stateToken = ScriptApp.newStateToken().withMethod("odooAuthCallback").withTimeout(3600).createToken();
    var redirectToAddon = "https://script.google.com/macros/d/".concat(scriptId, "/usercallback");
    var scope = ODOO_AUTH_URLS.SCOPE;
    var url =
        odooUrl +
        ODOO_AUTH_URLS.AUTH_CODE +
        (0, encodeQueryData)({
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
var getAccessToken = function () {
    var userProperties = PropertiesService.getUserProperties();
    var accessToken = userProperties.getProperty("ODOO_ACCESS_TOKEN");
    if (!accessToken || !accessToken.length) {
        return;
    }
    return accessToken;
};
/**
 * Reset the access token saved in the user properties.
 */
var resetAccessToken = function () {
    var userProperties = PropertiesService.getUserProperties();
    userProperties.deleteProperty("ODOO_ACCESS_TOKEN");
};
/**
 * Make an HTTP request to "/mail_plugin/auth/access_token" (cors="*") on the Odoo
 * database to verify that the server is reachable and that the mail plugin module is
 * installed.
 *
 * Returns True if the Odoo database is reachable and if the "mail_plugin" module
 * is installed, false otherwise.
 */
var isOdooDatabaseReachable = function (odooUrl) {
    if (!odooUrl || !odooUrl.length) {
        return false;
    }
    var response = (0, postJsonRpc)(
        odooUrl + ODOO_AUTH_URLS.CODE_VALIDATION,
        { auth_code: null },
        {},
        { returnRawResponse: true },
    );
    if (!response) {
        return false;
    }
    var responseCode = response.getResponseCode();
    if (responseCode > 299 || responseCode < 200) {
        return false;
    }
    return true;
};
