import * as React from "react";
import Partner from "../../../classes/Partner";
import {ContentType, HttpVerb, sendHttpRequest} from "../../../utils/httpRequest";
import PartnerData from "../../../classes/Partner";
import api from "../../api";
import ContactList from "../Contact/ContactList/ContactList";
import AppContext from '../AppContext';
import {Spinner, SpinnerSize} from "office-ui-fabric-react";
import {OdooTheme} from "../../../utils/Themes";
import {faSearch} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {TextField} from "office-ui-fabric-react/lib-amd";
import { _t } from "../../../utils/Translator";

const MAX_PARTNERS = 30;

type SearchProps = {
    query?: string,
    onPartnerClick: (partner: Partner, historyState?: SearchState) => void,
    historyState?: any
};

export type SearchState = {
    query: string,
    foundPartners?: Partner[],
    isLoading: boolean
}

class Search extends React.Component<SearchProps, SearchState> {

    constructor(props, context) {
        super(props, context);
        let query = "";
        if (props.historyState)
        {
            this.state = {...props.historyState};
        }
        else
        {
            if (props.query)
            {
                query = props.query;
            }
            this.state = {
                query: query,
                foundPartners: undefined,
                isLoading: true
            }
        }
    }

    private cancelOnGoingRequest = () => {
        if (this.onGoingRequest)
            this.onGoingRequest.cancel();
    };

    private getCurrentHistoryState = () => {
        if (this.state.isLoading)
        {
            return {query: this.state.query, foundPartners: undefined, isLoading: true} as SearchState;
        }
        else
        {
            return {...this.state} as SearchState;
        }
    }

    private getPartnersRequest = (query: String) => {
        this.setState({isLoading: true});
        this.cancelOnGoingRequest();
        if (query.length > 0)
        {
            this.onGoingRequest = sendHttpRequest(HttpVerb.POST,
                api.baseURL + api.searchPartner, ContentType.Json,
                this.context.getConnectionToken(), {
                    search_term: query,
                }, true);
            this.context.addRequestCanceller(this.onGoingRequest);
            this.onGoingRequest.promise.then(response => {
                const parsed = JSON.parse(response);
                let partners = parsed.result.partners.map(partner_json =>
                    {
                        return PartnerData.fromJSON(partner_json);
                    }
                );
                this.setState({foundPartners: partners, isLoading: false});
            }).catch((error) => {
                this.setState({foundPartners: [], isLoading: false});
                this.context.showHttpErrorMessage(error);
            });
        }
        else
        {
            this.setState({foundPartners: [], isLoading: false});
        }
    }

    private onKeyDown = (event) => {
        if (event.key == 'Enter')
            this.getPartnersRequest(this.state.query);
    }

    private onGoingRequest: {promise: Promise<any>, cancel: () => void};

    private onPartnerClick = (partner) => {
        this.props.onPartnerClick(partner, this.getCurrentHistoryState());
    }

    private onQueryChanged = (event) => {
        let query = event.target.value;
        this.setState({query: query});
    }

    componentDidMount() {
        if (this.state.isLoading)
            this.getPartnersRequest(this.state.query);
    }

    render() {

        let searchBar = (
            <div style={{display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "stretch", margin: "8px 8px 16px 8px"}}>
                <TextField className="input-search" placeholder={_t('Search contact in Odoo...')}
                       onChange={this.onQueryChanged} value={this.state.query} onKeyDown={this.onKeyDown}
                       onFocus={(e) => e.target.select()}
                />
                <div className="odoo-muted-button" style={{height: "100%", borderLeft: "none"}}
                     onClick={() => this.getPartnersRequest(this.state.query)}>
                    <FontAwesomeIcon icon={faSearch}/>
                </div>
            </div>
        );

        let resultsView = null;
        if (this.state.isLoading)
        {
            resultsView = (<div className="section-card" style={{padding: "32px"}}>
                <Spinner theme={OdooTheme} size={SpinnerSize.large} style={{margin: "auto"}}/>
            </div>);
        }
        else
        {
            let foundContactsNumberText = this.state.foundPartners.length >= MAX_PARTNERS ?
                "30+" : this.state.foundPartners.length.toString();
            if (this.state.foundPartners)
            resultsView = (
                <div className="section-card">
                    <div className="section-top">
                        <div className="custom-section-title-container">
                            <div className="section-title-text custom">
                                {_t("Contacts Found (%(count)s)", {
                                    count: foundContactsNumberText
                                })}
                            </div>
                        </div>
                    </div>
                    <div className="section-content">
                        <ContactList partners={this.state.foundPartners}
                                     onItemClick={this.onPartnerClick}/>
                    </div>
                </div>
            );
        }

        return (
          <div>
              {searchBar}
              {resultsView}
          </div>
        );
    }
}

Search.contextType = AppContext;

export default Search;