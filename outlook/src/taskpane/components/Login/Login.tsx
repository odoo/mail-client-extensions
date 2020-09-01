import * as React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHandshake, faEnvelope, faSearch } from '@fortawesome/free-solid-svg-icons'
import { TextField } from "office-ui-fabric-react/lib/TextField";
import { PrimaryButton, DefaultButton } from "office-ui-fabric-react";
import {HttpVerb, sendHttpRequest, ContentType} from "../../../utils/httpRequest";
import api from "../../api";
import AppContext from '../AppContext';
import "./Login.css";

type LoginProps = {};
type LoginState = { 
    isLoading: boolean;
    baseURL: string;
    urlError: string;
};
class Login extends React.Component<LoginProps, LoginState> {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            baseURL: localStorage.getItem("baseURL"),
            urlError: null
        };
    }

  onServerChange = (_, newValue?: string): void => {
        this.setState({
            baseURL: newValue,
            urlError: null
        });
    }

    sanitizeDbUrl = (urlStr: string): string => {
        let tmpStr = urlStr;
        // Without the protocol URL won't parse it.
        if (!tmpStr.startsWith('http://') && !tmpStr.startsWith('https://')) {
            tmpStr = 'https://' + tmpStr;
        }
        const url = new URL(tmpStr);
        url.protocol = 'https:';
        return url.origin;
    }

    login = () => {
        let sanitizedURL = '';
        try {
            sanitizedURL = this.sanitizeDbUrl(this.state.baseURL);
        } catch (err) {
            this.setState({urlError: 'The database URL is invalid. It should follow the scheme \'https://mycompany.odoo.com\''})
            return;
        }

        //const context = React.useContext(AppContext);
        api.baseURL = sanitizedURL;
        localStorage.setItem('baseURL', sanitizedURL)
        const options = {
        height: 65,
        width: 30,
        promptBeforeOpen: true,
        };

        const redirectToAddin = encodeURIComponent(api.addInRedirect);
        const redirectToAuthPage = encodeURIComponent(api.authCodePage + '?scope=' + api.outlookScope + '&friendlyname=' + api.outlookFriendlyName + '&info=some info' + '&redirect=' + redirectToAddin);
        const loginURL = api.baseURL + api.loginPage + '?redirect=' + redirectToAuthPage;

        Office.context.ui.displayDialogAsync(window.location.origin + '/dialog.html?dialogredir=' + loginURL, options , (asyncResult) => {
            console.log(asyncResult);
            let dialog = asyncResult.value;
            dialog.addEventHandler(Office.EventType.DialogMessageReceived, (_arg) => {
                dialog.close();
                let code = new URL(JSON.parse(_arg['message']).value).searchParams.get("auth_code");
                sendHttpRequest(HttpVerb.POST, api.baseURL + api.getAccessToken, ContentType.Json, null, {"auth_code": code}, true)
                .promise.then((response) => {
                    const parsed = JSON.parse(response);
                    this.context.connect(parsed.result.access_token);
                    this.context.navigation.goToMain();
                });
            });
        })
    };

    signup = () => {
        window.open('https://www.odoo.com/trial?selected_app=mail_client_extension','_blank');
    }

    render() {
    
    return (
        <>
            <div className='lower-bounded-tile'>
                <span className='link-like-button' onClick={this.context.navigation.goToMain} >&larr; BACK</span>
            </div>
            
            <div className='bounded-tile'>
                <div style={{fontSize: '30px', width: '200px', margin:'auto', textAlign:'center'}}>Connect Your <img src='../../../../assets/odoo-full.png' style={{height: '30px'}}/> Database</div>
                <TextField
                    className="form-line"
                    label="Database URL"
                    placeholder="E.g. : https://mycompany.odoo.com"
                    defaultValue={this.state.baseURL}
                    onChange={this.onServerChange}
                    errorMessage={this.state.urlError}
                />
                <PrimaryButton className="form-line full-width odoo-filled-button" text='Login' onClick={this.login}/>

                <h3 className='horizontal-line'><span>OR</span></h3>

                <DefaultButton className="full-width odoo-clear-button" text='Sign up' onClick={this.signup}/>

                <div className='login-info'>
                    <div className='login-info-icon'><FontAwesomeIcon icon={faEnvelope} size="2x" /></div>
                    <div>Create leads from Emails sent to your personal email address.</div>
                </div>
                <div className='login-info'>
                    <div className='login-info-icon'><FontAwesomeIcon icon={faHandshake} size="2x" /></div>
                    <div>Centralize Prospects&apos; emails into a CRM.</div>
                </div>
                <div className='login-info'>
                    <div className='login-info-icon'><FontAwesomeIcon icon={faSearch} size="2x" /></div>
                    <div>Search and store insights on your contacts.</div>
                </div>
            </div>
        </>
    );
    }
}
Login.contextType = AppContext;
export default Login;
