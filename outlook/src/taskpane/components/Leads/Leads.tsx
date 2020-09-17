import * as React from 'react';
import api from "../../api";
import LeadList from './LeadList/LeadList';
import LeadData from '../../../classes/Lead';
import AppContext from '../AppContext';
import { HttpVerb, sendHttpRequest, ContentType } from "../../../utils/httpRequest";


type LeadsProps = {};
type LeadsState = {
    leads: LeadData[],
    loaded: boolean,
    showMore: boolean
};

class Leads extends React.Component<LeadsProps, LeadsState> {
    leadOffset = 0;
    leadLimit = 5;
    constructor(props) {
        super(props);
        this.state = { 
            leads: [],
            loaded: false,
            showMore: true
        };
    }

    loadLeads = () => {
        const requestJson = {
            partner: this.context.partner.id,
            offset: this.leadOffset,
            limit: this.leadLimit
        }
        const cancellableRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.getLeads, ContentType.Json, this.context.getConnectionToken(), requestJson, true);
        this.context.addRequestCanceller(cancellableRequest.cancel);
        cancellableRequest.promise.then((response) => {
            const parsed = JSON.parse(response);
            const leadsCopy = this.state.leads.map(lead => LeadData.copy(lead));
            const newLeads = parsed.result.leads.map(l => {return LeadData.fromJSON(l);})
            const allLeads = leadsCopy.concat(newLeads)
            this.setState({leads: allLeads, loaded: true, showMore: newLeads.length === this.leadLimit})
        }).catch(function(error) {
            console.log("Error catched: " + error);
        })
    }

    loadMore = () => {
        // If the length is already smaller to the limit, there is nothing more to load.
        // So let's not grow leadLimit indefinitely, who knows...
        if (this.state.leads.length === this.leadLimit) {
            this.leadOffset += this.leadLimit;
            this.loadLeads();
        }
    }

    log = (leadId: number) => {
        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, (result) => {
        const msgHeader = '<div>From: '+ Office.context.mailbox.item.sender.emailAddress + '</div><br/>';
        const msgFooter = '<br/><div class="text-muted font-italic">Logged from <a href="https://www.odoo.com/documentation/user/crm/optimize/mail_client_extension.html" target="_blank">Outlook Inbox</a></div>';
        const message = msgHeader + result.value + msgFooter;
        const requestJson = {
            lead: leadId,
            message: message
        }
        const cancellableRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.logMail, ContentType.Json, this.context.getConnectionToken(), requestJson, true);
        this.context.addRequestCanceller(cancellableRequest.cancel);
        cancellableRequest.promise.then((response) => {
            const parsed = JSON.parse(response); 
            if (parsed['error']){
                // TODO error message on the top, such messages should be in the context.
                return;
            }
            const leadsCopy = this.state.leads.map(lead => {
                const copy = LeadData.copy(lead);
                if (lead.id === leadId) {
                copy.logged = true;
                }
                return copy;
            });
            this.setState({leads: leadsCopy})
        }).catch(function(error) { console.log("Error catched: " + error); })
        })
    }

    goToLeadForm = () => {
        window.open(api.baseURL + api.redirectCreateLead + '?partner_id=' + this.context.partner.id,"_blank");
    }

    public render(): JSX.Element {
        // Modules are loaded asynchronously and crm is displayed before the partner is populated.
        if (this.state.loaded === false && this.context.partner.id !== -1) {
            this.loadLeads();
        }

        /*
            {this.context.partner.id !== -1 && !this.state.leads.length ? <div>None found</div> : null}
            {this.context.partner.id === -1 ? <div>Add the contact to your database to be able to create opportunities</div> : null}
            {this.state.leads.length ? <LeadList leads={this.state.leads} more={this.loadMore} log={this.log} showMore={this.state.showMore}></LeadList> : null}
        */
        let content = <div>None found</div>;
        if (this.state.leads.length) {
            content = <LeadList leads={this.state.leads} more={this.loadMore} log={this.log} showMore={this.state.showMore}></LeadList>;
        } else if (this.context.partner.id === -1) {
            content = <div>Add the contact to your database to be able to create opportunities</div>
        }

        return (
            <>
                <div className='tile-title-space'>
                    <div className='tile-title'>
                    <div className='text'>OPPORTUNITIES</div>
                    {this.context.partner.id !== -1 ? <div className='button' onClick={this.goToLeadForm}>New</div> : null}
                    </div>
                </div>

                <div className='bounded-tile'>
                    {content}
                </div>
            </>
        );
    }
}

Leads.contextType = AppContext;
export default Leads;