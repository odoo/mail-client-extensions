import * as React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHandshake, faEnvelope, faSearch, faLifeRing } from '@fortawesome/free-solid-svg-icons';
import { TextField } from 'office-ui-fabric-react/lib/TextField';
import { PrimaryButton, DefaultButton, Spinner, SpinnerSize } from 'office-ui-fabric-react';
import { HttpVerb, sendHttpRequest, ContentType } from '../../../utils/httpRequest';
import 'fontawesome-4.7/css/font-awesome.css';
import api from '../../api';
import AppContext from '../AppContext';
import './Login.css';
import { OdooTheme } from '../../../utils/Themes';

/**
 * Error which can occurs during the authentication process.
 */
enum AuthenticationRequestError {
    None,
    InvalidScheme,
    DatabaseNotReachable,
    PermissionRefused,
    AuthenticationCodeExpired,
}

type LoginState = {
    isCheckingUrl: boolean;
    isLoading: boolean;
    baseURL: string;
    authenticationRequestError: AuthenticationRequestError;
};

class Login extends React.Component<{}, LoginState> {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            baseURL: localStorage.getItem('baseURL'),
            authenticationRequestError: AuthenticationRequestError.None,
            isCheckingUrl: false,
        };
    }

    onServerChange = (_, newValue?: string): void => {
        this.setState({
            baseURL: newValue,
            authenticationRequestError: AuthenticationRequestError.None,
            isCheckingUrl: false,
        });
    };

    sanitizeDbUrl = (urlStr: string): string => {
        try {
            let tmpStr = urlStr;
            // Without the protocol URL won't parse it.
            if (!tmpStr.startsWith('http://') && !tmpStr.startsWith('https://')) {
                tmpStr = 'https://' + tmpStr;
            }
            const url = new URL(tmpStr);
            url.protocol = 'https:';
            return url.origin;
        } catch {
            return null;
        }
    };

    login = async () => {
        this.setState({ isCheckingUrl: true });

        const sanitizedURL = this.sanitizeDbUrl(this.state.baseURL);
        if (!sanitizedURL) {
            this.setState({
                isCheckingUrl: false,
                authenticationRequestError: AuthenticationRequestError.InvalidScheme,
            });
            return;
        }

        this.setState({ baseURL: sanitizedURL });
        api.baseURL = sanitizedURL;
        localStorage.setItem('baseURL', sanitizedURL);

        if (!(await this._isOdooDatabaseReachable())) {
            this.setState({
                isCheckingUrl: false,
                authenticationRequestError: AuthenticationRequestError.DatabaseNotReachable,
            });
            return;
        }

        this.setState({ isCheckingUrl: false });

        const authCode = await this._openOdooLoginDialog();
        if (!authCode) {
            this.setState({
                authenticationRequestError: AuthenticationRequestError.PermissionRefused,
            });
            return;
        }

        const accessToken = await this._exchangeAuthCodeForAccessToken(authCode);
        if (!accessToken) {
            this.setState({
                authenticationRequestError: AuthenticationRequestError.AuthenticationCodeExpired,
            });
            return;
        }

        this.setState({ authenticationRequestError: AuthenticationRequestError.None });

        this.context.connect(accessToken);
        this.context.navigation.goToMain();
    };

    /**
     * Check if the database URL is correct and if the mail plugin is installed
     * by requesting the endpoint "/mail_plugin/auth/access_token" (with cors="*" !).
     *
     * If the URL is not reachable (invalid URL or the Odoo module is not installed)
     * return false.
     */
    _isOdooDatabaseReachable = async () => {
        const request = sendHttpRequest(
            HttpVerb.POST,
            api.baseURL + api.getAccessToken,
            ContentType.Json,
            null,
            {},
            true,
        );

        try {
            await request.promise;
            return true;
        } catch {
            return false;
        }
    };

    /**
     * Open a dialog and ask the permission on the Odoo side.
     *
     * Return null if the user refused the permission and return the authentication
     * code if the user accepted the permission.
     */
    _openOdooLoginDialog = async () => {
        const options = {
            height: 65,
            width: 30,
            promptBeforeOpen: true,
        };

        const redirectToAddin = encodeURIComponent(api.addInBaseURL + '/taskpane.html');
        const redirectToAuthPage = encodeURIComponent(
            api.authCodePage +
                '?scope=' +
                api.outlookScope +
                '&friendlyname=' +
                api.outlookFriendlyName +
                '&redirect=' +
                redirectToAddin,
        );
        const loginURL = api.baseURL + api.loginPage + '?redirect=' + redirectToAuthPage;
        const url = `${api.addInBaseURL}/dialog.html?dialogredir=${loginURL}`;

        return new Promise((resolve, _) => {
            Office.context.ui.displayDialogAsync(url, options, (asyncResult) => {
                const dialog = asyncResult.value;
                dialog.addEventHandler(Office.EventType.DialogMessageReceived, (_arg) => {
                    dialog.close();
                    const searchParams = new URL(JSON.parse(_arg['message']).value).searchParams;
                    const success = searchParams.get('success');
                    if (success === '1') {
                        const authCode = searchParams.get('auth_code');
                        resolve(authCode && authCode.length ? authCode : null);
                    } else {
                        resolve(null);
                    }
                });
            });
        });
    };

    /**
     * Make an HTTP request to the Odoo database to exchange the authentication code
     * for a long term access token.
     *
     * Return the access token or null if something went wrong.
     */
    _exchangeAuthCodeForAccessToken = async (authCode) => {
        try {
            return sendHttpRequest(
                HttpVerb.POST,
                api.baseURL + api.getAccessToken,
                ContentType.Json,
                null,
                { auth_code: authCode },
                true,
            ).promise.then((response) => {
                const parsed = JSON.parse(response);
                const accessToken = parsed.result.access_token;
                return accessToken && accessToken.length ? accessToken : null;
            });
        } catch {
            return null;
        }
    };

    signup = () => {
        window.open(
            'https://www.odoo.com/trial?selected_app=mail_plugin:crm_mail_plugin:helpdesk_mail_plugin',
            '_blank',
        );
    };

    render() {
        const errorMessage = this._getErrorMessage();

        return (
            <>
                <div className="lower-bounded-tile">
                    <span className="link-like-button" onClick={this.context.navigation.goToMain}>
                        &larr; BACK
                    </span>
                </div>

                <div className="bounded-tile">
                    <div className="connect-your-database">
                        Connect Your
                        <img src="assets/odoo-full.png" />
                        Database
                    </div>
                    <TextField
                        className="form-line"
                        label="Database URL"
                        placeholder="E.g. : https://mycompany.odoo.com"
                        value={this.state.baseURL}
                        onChange={this.onServerChange}
                        errorMessage={errorMessage ? ' ' : null}
                    />
                    {errorMessage}
                    {this._getLoggingButton()}
                    <h3 className="horizontal-line">
                        <span>OR</span>
                    </h3>
                    <DefaultButton className="full-width odoo-clear-button" text="Sign up" onClick={this.signup} />
                    <div className="login-info">
                        <div className="login-info-icon">
                            <FontAwesomeIcon icon={faEnvelope} size="2x" className="fa-fw" />
                        </div>
                        <div>Create leads from Emails sent to your personal email address.</div>
                    </div>
                    <div className="login-info">
                        <div className="login-info-icon">
                            <FontAwesomeIcon icon={faLifeRing} size="2x" className="fa-fw" />
                        </div>
                        <div>Create Tickets from Emails sent to your personal email address.</div>
                    </div>
                    <div className="login-info">
                        <div className="login-info-icon">
                            <FontAwesomeIcon icon={faHandshake} size="2x" className="fa-fw" />
                        </div>
                        <div>Centralize Prospects&apos; emails into a CRM.</div>
                    </div>
                    <div className="login-info">
                        <div className="login-info-icon">
                            <i className="fa fa-tasks fa-fw fa-2x"></i>
                        </div>
                        <div>Create Tasks from Emails sent to your personal email address.</div>
                    </div>
                    <div className="login-info">
                        <div className="login-info-icon">
                            <FontAwesomeIcon icon={faSearch} size="2x" className="fa-fw" />
                        </div>
                        <div>Search and store insights on your contacts.</div>
                    </div>
                </div>
            </>
        );
    }

    /**
     * Check the "authenticationRequestError" state and return the appropriate error message.
     */
    _getErrorMessage = () => {
        const ERROR_MESSAGES = {
            [AuthenticationRequestError.InvalidScheme]:
                'The database URL is invalid. It should follow the scheme "https://mycompany.odoo.com". ',
            [AuthenticationRequestError.DatabaseNotReachable]:
                'Could not connect to your database. Make sure the module is installed in Odoo (Settings > General Settings > Integrations > Mail Plugins). ',
            [AuthenticationRequestError.PermissionRefused]: 'Permission to access your database needs to be granted. ',
            [AuthenticationRequestError.AuthenticationCodeExpired]:
                'Your authentication code is invalid or has expired. ',
        };

        const errorStr = ERROR_MESSAGES[this.state.authenticationRequestError];
        if (errorStr) {
            return (
                <span className="error-text">
                    {errorStr}
                    See our
                    <a
                        href="https://www.odoo.com/documentation/master/applications/productivity/mail_plugins.html"
                        target="_blank">
                        FAQ
                    </a>
                    .
                </span>
            );
        }
        return null;
    };

    /**
     * Return the logging button with the appropriate label.
     */
    _getLoggingButton = () => {
        if (this.state.isCheckingUrl) {
            return (
                <PrimaryButton className="form-line full-width odoo-filled-button">
                    <Spinner size={SpinnerSize.small} className="login-spinner" theme={OdooTheme} />
                    <span>Connecting</span>
                </PrimaryButton>
            );
        }
        return <PrimaryButton className="form-line full-width odoo-filled-button" text="Login" onClick={this.login} />;
    };
}
Login.contextType = AppContext;
export default Login;
