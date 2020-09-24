import * as React from "react";

import "./Main.css";

import { Link, MessageBar, MessageBarType} from 'office-ui-fabric-react';

import Contact from '../Contact/Contact';
import Company from '../Company/Company';
import Leads from "../Leads/Leads";
import GrayOverlay from "../GrayOverlay";

import { HttpVerb, sendHttpRequest, ContentType } from "../../../utils/httpRequest";
import api from "../../api";

import PartnerData from "../../../classes/Partner";
import EnrichmentInfo, {EnrichmentInfoType} from '../../../classes/EnrichmentInfo';
import CompanyCache from "../../../classes/CompanyCache";
import CompanyData from "../../../classes/Company";

import AppContext from '../AppContext';

enum Page {
    Main,
}

type MainProps = {};
type MainState = {
    pageDisplayed: Page,
    showPartnerCreatedMessage: boolean;
    showEnrichmentInfoMessage: boolean;
    EnrichmentInfo: EnrichmentInfo,
    partnerCreated: Boolean,
};

class Main extends React.Component<MainProps, MainState> {
    connectionToken : string;
    companyCache : CompanyCache;

    constructor(props) {
        super(props);
        this.state = {
            pageDisplayed: Page.Main,
            showPartnerCreatedMessage: false,
            showEnrichmentInfoMessage: false,
            EnrichmentInfo: new EnrichmentInfo(),
            partnerCreated: false,
        };

        this.companyCache = new CompanyCache(1, 200, 25); // TODO param somewhere
    }

    componentDidMount() {
        this.loadOrReload();
    }

    _connectedFlow = () => {
        if (!Office.context.mailbox.item) {
            return;
        }
        
        const email = Office.context.mailbox.item.from.emailAddress;
        const displayName = Office.context.mailbox.item.from.displayName;
        this.context.setIsLoading(true);

        const cancellablePartnerRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.getPartner, ContentType.Json, this.context.getConnectionToken(), {
            email: email,
            name: displayName
        }, true);
        this.context.addRequestCanceller(cancellablePartnerRequest.cancel);
        cancellablePartnerRequest.promise.then(response => {
            const parsed = JSON.parse(response);
            var partner = PartnerData.fromJSON(parsed.result.partner);
            this.setState({
                EnrichmentInfo: EnrichmentInfo.fromJSON(parsed.result['enrichment_info']),
                partnerCreated: parsed.result['created'],
                showEnrichmentInfoMessage: true,
                showPartnerCreatedMessage: true
            });
            this.context.setPartner(partner, false);
        }).catch((error) => {
            console.log("Error catched: " + error);
            if (error.message == '0') {
                this.setState({
                    EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.ConnectionError),
                    showEnrichmentInfoMessage: true
                });
            } else {
                this.setState({
                    EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.Other),
                    showEnrichmentInfoMessage: true
                });    
            }
            this.context.setPartner(new PartnerData(), false);
        });

        const cancellableRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.getInstalledModules, ContentType.Json, this.context.getConnectionToken(), {})
        this.context.addRequestCanceller(cancellableRequest.cancel);
        cancellableRequest.promise.then(response => {
            const parsed = JSON.parse(response);
            this.context.setModules(parsed.result.modules);
        }).catch(function(error) {
            console.log("Error catched: " + error);
        });
    }

  _disconnectedFlow() {
    Office.context.mailbox.getUserIdentityTokenAsync(idTokenResult=>{
        const userEmail = Office.context.mailbox.userProfile.emailAddress;
        const senderEmail = Office.context.mailbox.item.from.emailAddress;
        const senderDisplayName = Office.context.mailbox.item.from.displayName;
        const senderDomain = senderEmail.split('@')[1];

        const partner = new PartnerData();
        partner.email = senderEmail;
        partner.name = senderDisplayName;

        const cachedCompany : CompanyData = this.companyCache.get(senderEmail)

        this.context.setIsLoading(true);
        // Check the cache before calling the IAP.
        if (cachedCompany) {
            partner.company = cachedCompany;
            this.setState({ EnrichmentInfo: new EnrichmentInfo() });
            this.context.setPartner(partner, false);
        } else {
            const cancellableRequest = sendHttpRequest(HttpVerb.POST, api.iapLeadEnrichment, ContentType.Json, null, {"params": {
            "email": userEmail,
            "domain": senderDomain,
            "extuid": idTokenResult.value
            }})
            this.context.addRequestCanceller(cancellableRequest.cancel);
            cancellableRequest.promise.then(response => {
                const parsed = JSON.parse(response);
                if ('error' in parsed) {
                    this.setState({ 
                        EnrichmentInfo: new EnrichmentInfo(parsed.error.data.exception_type) ,
                        showEnrichmentInfoMessage: true
                    });
                    this.context.setPartner(partner, false);
                    return;
                }
                const company = CompanyData.fromRevealJSON(parsed.result);
                partner.company = company;
                this.companyCache.add(company);
                this.setState({ EnrichmentInfo: new EnrichmentInfo() });
                this.context.setPartner(partner, false);
            }).catch(error => {
                console.log("Error catched: " + error);
                if (error.message == '0') {
                    this.setState({
                        EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.ConnectionError),
                        showEnrichmentInfoMessage: true
                    });
                } else {
                    this.setState({
                        EnrichmentInfo: new EnrichmentInfo(EnrichmentInfoType.Other),
                        showEnrichmentInfoMessage: true
                    });    
                }
                // At least the info present in the mail will be displayed, not an empty screen.
                this.context.setPartner(partner, false);
            });
        }
            
        });
    }

    _hideEnrichmentInfoMessage = () => {
        this.setState({
            showEnrichmentInfoMessage: false
        })
    }

    _hidePartnerCreatedMessage = () => {
        this.setState({
            showPartnerCreatedMessage: false
        })
    }

    _getMessageBars = () => {
        const {type, info} = this.state.EnrichmentInfo;
        let bars = [];
        if (this.state.showPartnerCreatedMessage && this.state.partnerCreated) {
            bars.push(<MessageBar messageBarType={MessageBarType.success} onDismiss={this._hidePartnerCreatedMessage}>Contact created</MessageBar>);
            //setTimeout(this._hidePartnerCreatedMessage, 3000);
        }
        if (this.state.showEnrichmentInfoMessage) {
            switch (type) {
            case EnrichmentInfoType.CompanyCreated:
                bars.push(<MessageBar messageBarType={MessageBarType.success} onDismiss={this._hideEnrichmentInfoMessage}>Company created</MessageBar>);
                //setTimeout(this._hideEnrichmentInfoMessage, 3500);
                break;
            case EnrichmentInfoType.NoData:
                bars.push(<MessageBar messageBarType={MessageBarType.info} onDismiss={this._hideEnrichmentInfoMessage}>{info}</MessageBar>);
                break;
            case EnrichmentInfoType.InsufficientCredit:
                bars.push(<MessageBar messageBarType={MessageBarType.error} onDismiss={this._hideEnrichmentInfoMessage}>
                    Could not auto-complete the company: not enough credits!
                    <Link href={info} target="_blank">
                        Buy More
                    </Link>
                </MessageBar>);
                break;
            case EnrichmentInfoType.NotConnected_InsufficientCredit:
            case EnrichmentInfoType.NotConnected_InternalError:
            case EnrichmentInfoType.Other:
            case EnrichmentInfoType.ConnectionError:
                bars.push(<MessageBar messageBarType={MessageBarType.error} onDismiss={this._hideEnrichmentInfoMessage}>{info}</MessageBar>);
                break;
            }
        }
        return bars;
    }

    loadOrReload = () => {
        this.context.cancelRequests();
        if (this.context.isConnected()) {
            this._connectedFlow();
        } else {
            this._disconnectedFlow();
        }
    }

    render() {
        // Bad.
        if (this.context.doReload) {
            this.context.setDoReload(false);
            this.loadOrReload();
            return null;
        }


        switch(this.state.pageDisplayed)
        {
            case Page.Main:
            let connectionButton = <div className='link-like-button connect-button' onClick={() => this.context.navigation.goToLogin()}>Login</div>;
            if (this.context.isConnected()){
                connectionButton = <div className='link-like-button connect-button' onClick={() =>{this.context.disconnect();this.context.navigation.goToLogin();}}>Logout</div>
            }

            // In the normal disconnected flow, the company will be -1 and every info will be in additionalInfo.
            // In that case Company should show up, it's designed to get the necessary info in addditionalInfo if not found elsewhere.
            // In case of error with the IAP in non connected mode the company id will be -1 and additionalInfo === {}
            // Then and only then the Company should not show.
            return (
                <>
                    {this.context.isLoading ? <GrayOverlay></GrayOverlay> : null}
                    <div className='message-bars'>
                        {this._getMessageBars()}
                    </div>
                    <Contact />
                    {this.context.modules.includes('crm') ? <Leads /> : null}
                    {this.context.partner.company.id !== -1 || Object.keys(this.context.partner.company.additionalInfo).length !== 0 ? <Company /> : null}
                    {connectionButton}
                    
                </>
            );
        }
    }
}
Main.contextType = AppContext;

export default Main;
