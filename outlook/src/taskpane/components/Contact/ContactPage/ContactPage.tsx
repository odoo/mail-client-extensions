import * as React from "react";
import Partner from "../../../../classes/Partner";
import PartnerData from "../../../../classes/Partner";
import AppContext from '../../AppContext';
import LeadsSection from "../../Crm/LeadsSection/LeadsSection";
import ContactSection from "../ContactSection/ContactSection";
import CompanySection from "../../Company/CompanySection/CompanySection";
import TicketsSection from "../../Helpdesk/TicketsSection/TicketsSection";
import {ContentType, HttpVerb, sendHttpRequest} from "../../../../utils/httpRequest";
import api from "../../../api";
import EnrichmentInfo, {EnrichmentInfoType} from "../../../../classes/EnrichmentInfo";
import {Spinner, SpinnerSize} from "office-ui-fabric-react";
import {OdooTheme} from "../../../../utils/Themes";
import "./ContactPage.css";
import Lead from "../../../../classes/Lead";
import HelpdeskTicket from "../../../../classes/HelpdeskTicket";
import TasksSection from "../../Project/TasksSection/TasksSection";
import Task from "../../../../classes/Task";


type ContactPageProps = {
    partner: Partner;
    onPartnerChanged?: (Partner) => void;
    loadPartner: boolean;
};

type ContactPageState = {
    partner: Partner;
    isLoading: boolean;
};


class ContactPage extends React.Component<ContactPageProps, ContactPageState> {
    constructor(props, context) {
        super(props, context);
        this.state = {partner: props.partner, isLoading: true};
    }

    private fetchContact = () => {

        const partner = this.props.partner;

        let requestData = !this.props.partner.isAddedToDatabase() ? {email: partner.email, name: partner.name}
            : {partner_id: partner.id}

        const partnerRequest = sendHttpRequest(HttpVerb.POST,
            api.baseURL + api.getPartner, ContentType.Json,
            this.context.getConnectionToken(), requestData, true);

        this.context.addRequestCanceller(partnerRequest.cancel);

        partnerRequest.promise.then(response => {
            const parsed = JSON.parse(response);
            let partner = PartnerData.fromJSON(parsed.result.partner);
            if (parsed.result.leads)
            {
                partner.leads = parsed.result.leads.map(lead_json => Lead.fromJSON(lead_json));
            }
            if (parsed.result.tasks) {
                partner.tasks = parsed.result.tasks.map(task_json => Task.fromJSON(task_json));
            }
            if (parsed.result.tickets)
            {
                partner.tickets = parsed.result.tickets.map(ticket_json => HelpdeskTicket.fromJSON(ticket_json));
            }
            if (parsed.result.user_companies) {
                this.context.setUserCompanies(parsed.result.user_companies);
            }
            this.setState({partner: partner, isLoading: false});
            if (parsed.result.partner['enrichment_info'])
            {
                const enrichmentInfo = new EnrichmentInfo(parsed.result.partner['enrichment_info'].type,
                    parsed.result.partner['enrichment_info'].info);
                if (enrichmentInfo.type != EnrichmentInfoType.NoData)
                    this.context.showTopBarMessage(enrichmentInfo);
            }
            this.propagatePartnerInfoChange(partner);
        }).catch(error => {
            this.context.showHttpErrorMessage(error);
            this.setState({isLoading: false});
            console.log(error);
        });
    }

    private isCrmInstalled = ():boolean => {
        return (this.props.partner.leads != undefined);
    }

    private isProjectInstalled = ():boolean => {
        return (this.props.partner.tasks != undefined);
    }

    private isHelpdeskInstalled =():boolean => {
        return (this.props.partner.tickets != undefined);
    }

    private propagatePartnerInfoChange = (partner: Partner) => {
        this.setState({partner: partner});
        this.props.onPartnerChanged(partner);
    }

    componentDidMount() {
        if (this.props.loadPartner && this.context.isConnected())
            this.fetchContact();
        else
            this.setState({isLoading: false, partner: this.props.partner});
    }

    render() {

        if (this.state.isLoading)
        {
            return (
                <>
                    <div className="spinner-container">
                        <Spinner size={SpinnerSize.large} theme={OdooTheme}/>
                    </div>
                </>
            );
        }
        else
        {
            let leadsList = null;
            if (this.isCrmInstalled())
            {
                leadsList = (<div style={{marginTop: "16px"}}><LeadsSection partner={this.state.partner}/></div>);
            }

            let tasksList = null;
            if (this.isProjectInstalled()) {
                tasksList = (<div style={{marginTop: "16px"}}><TasksSection partner={this.state.partner}/></div>);
            }

            let ticketsList = null;
            if (this.isHelpdeskInstalled())
            {
                ticketsList = (<div style={{marginTop: "16px"}}><TicketsSection partner={this.state.partner}/></div>)
            }

            let hideCollapseButton = (!this.isHelpdeskInstalled() && !this.isCrmInstalled());

            return (
                <>
                    <ContactSection partner={this.state.partner}/>
                    {leadsList}
                    {tasksList}
                    {ticketsList}
                    <div style={{marginTop: "16px"}}>
                        <CompanySection partner={this.state.partner} onPartnerInfoChanged={this.propagatePartnerInfoChange}
                                        hideCollapseButton={hideCollapseButton}/>
                    </div>
                </>
            )
        }
    }
}

ContactPage.contextType = AppContext;

export default ContactPage;