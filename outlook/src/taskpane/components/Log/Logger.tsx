import * as React from "react";
import {ContentType, HttpVerb, sendHttpRequest} from "../../../utils/httpRequest";
import AppContext from '../AppContext';
import api from "../../api";
import {Spinner, SpinnerSize, TooltipHost} from "office-ui-fabric-react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheck, faEnvelope} from "@fortawesome/free-solid-svg-icons";
import {OdooTheme} from "../../../utils/Themes";

type LoggerProps = {
    resId: number,
    model: string,
    tooltipContent: string
};

type LoggerState = {
    logged: number
}


class Logger extends React.Component<LoggerProps, LoggerState> {

    constructor(props, context) {
        super(props, context);
        this.state = {
            logged: 0
        };
    }

    private logRequest = (event) => {
        event.stopPropagation();

        this.setState({logged: 1});
        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, (result) => {
            const msgHeader = '<div>From: ' + Office.context.mailbox.item.sender.emailAddress + '</div><br/>';
            const msgFooter = '<br/><div class="text-muted font-italic">Logged from <a href="https://www.odoo.com/documentation/user/crm/optimize/mail_client_extension.html" target="_blank">Outlook Inbox</a></div>';
            const body = result.value.split('<div id="x_appendonsend"></div>')[0]; // Remove the history and only log the most recent message.
            const message = msgHeader + body + msgFooter;

            const requestJson = {
                res_id: this.props.resId,
                model: this.props.model,
                message: message
            }
            const logRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.logSingleMail, ContentType.Json,
                this.context.getConnectionToken(), requestJson, true);
            logRequest.promise.then(response => {
                const parsed = JSON.parse(response);
                if (parsed['error']) {
                    this.setState({logged: 0});
                    this.context.showHttpErrorMessage();
                    return;
                } else {
                    this.setState({logged: 2});
                }
            }).catch(error => {
                this.context.showHttpErrorMessage(error);
                this.setState({logged: 0});
            });
        });
    }

    render() {

        let logContainer = null;
        switch (this.state.logged)
        {
            case 0:
                logContainer = (
                    <div className="log-container">
                        <TooltipHost content={this.props.tooltipContent}>
                            <div className='odoo-secondary-button' onClick={this.logRequest} style={{width: "auto"}}>
                                <FontAwesomeIcon  icon={faEnvelope}/>
                            </div>
                        </TooltipHost>
                    </div>
                );
                break;
            case 1:
                logContainer = (
                    <div className="log-container">
                        <div>
                            <Spinner theme={OdooTheme} size={SpinnerSize.medium}/>
                        </div>
                    </div>
                )
                break;
            case 2:
                logContainer = (
                    <div className="log-container">
                        <div className="logged-text">
                            <FontAwesomeIcon  icon={faCheck} color={"green"}/>
                        </div>
                    </div>
                );
                break;
        }

        return (
            <>
                {logContainer}
            </>
        );
    }

}

Logger.contextType = AppContext;

export default Logger;