import * as React from 'react';
import { _t } from '../../../utils/Translator';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../utils/httpRequest';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { TextField, TooltipHost } from 'office-ui-fabric-react';
import { faArrowLeft, faRedoAlt, faSearch } from '@fortawesome/free-solid-svg-icons';
import AppContext from '../AppContext';
import HelpdeskTicket from '../../../classes/HelpdeskTicket';
import Lead from '../../../classes/Lead';
import Partner from '../../../classes/Partner';
import Task from '../../../classes/Task';
import api from '../../api';

type SearchRefrechProps = {
    title: string;
    partner: Partner;
    searchType: 'lead' | 'task' | 'ticket';
    setIsSearching: (isSearching: boolean) => void;
    setIsLoading: (isLoading: boolean) => void;
    updateRecords: (records: Lead[] | Task[] | HelpdeskTicket[]) => void;
};

type SearchRefrechState = {
    isSearching: boolean;
    query: string;
};

class SearchRefrech extends React.Component<SearchRefrechProps, SearchRefrechState> {
    constructor(props, context) {
        super(props, context);
        this.state = {
            isSearching: false,
            query: '',
        };
    }

    private onBackClick = () => {
        this.setState({ isSearching: !this.state.isSearching, query: '' });
        this.props.updateRecords(null);
        this.props.setIsSearching(false);
    };

    private onRefrechClick = () => {
        this.searchData();
    };

    private onSearchClick = () => {
        this.setState({ isSearching: true });
        this.props.setIsSearching(true);
    };

    private onKeyDown = (event) => {
        if (event.key == 'Enter') {
            if (!this.state.query.trim()) {
                return;
            }
            this.searchData(this.state.query);
        }
    };

    private getEndPoint = (params: string) => {
        let endPoint = '';
        if (this.props.searchType === 'lead') {
            endPoint = api.Leads;
        } else if (this.props.searchType === 'task') {
            endPoint = api.Tasks;
        } else {
            endPoint = api.Tickets;
        }
        return endPoint + `/${params}`;
    };

    private searchData = async (query?: string) => {
        this.props.setIsLoading(true);
        let endPoint = query ? this.getEndPoint('search') : this.getEndPoint('refresh');

        try {
            const res = sendHttpRequest(
                HttpVerb.POST,
                api.baseURL + endPoint,
                ContentType.Json,
                this.context.getConnectionToken(),
                { query: query, partner: this.props.partner },
                true,
            );
            const data = JSON.parse(await res.promise);

            if (this.props.searchType === 'lead') {
                data.result = data.result.map((lead: Lead) => Lead.fromJSON(lead));
            } else if (this.props.searchType === 'task') {
                data.result = data.result.map((task: Task) => Task.fromJSON(task));
            } else {
                data.result = data.result.map((ticket: HelpdeskTicket) => HelpdeskTicket.fromJSON(ticket));
            }
            if (data.result) {
                this.props.updateRecords(data.result);
            }
        } catch (error) {
            this.context.showHttpErrorMessage(error);
        } finally {
            this.props.setIsLoading(false);
        }
    };

    render() {
        let broadCampStyle = {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: 'medium',
            color: '#787878',
            fontWeight: 600,
        };

        let searchButton = null;
        let refrechButton = null;
        if (!this.state.isSearching) {
            searchButton = (
                <div style={{ display: 'flex' }}>
                    <TooltipHost content={_t(`Search ${this.props.title.slice(0, this.props.title.indexOf(' '))}`)}>
                        <div className="odoo-muted-button" onClick={this.onSearchClick} style={{ border: 'none' }}>
                            <FontAwesomeIcon icon={faSearch} />
                        </div>
                    </TooltipHost>
                </div>
            );
            refrechButton = (
                <TooltipHost content={_t(`Refresh ${this.props.title.slice(0, this.props.title.indexOf(' '))}`)}>
                    <div className="odoo-muted-button" onClick={this.onRefrechClick} style={{ border: 'none' }}>
                        <FontAwesomeIcon icon={faRedoAlt} />
                    </div>
                </TooltipHost>
            );
        }

        let backButton = null;
        let searchBar = null;
        if (this.state.isSearching) {
            backButton = (
                <div className="odoo-muted-button" onClick={this.onBackClick} style={{ border: 'none' }}>
                    <FontAwesomeIcon icon={faArrowLeft} />
                </div>
            );
            searchBar = (
                <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'stretch' }}>
                    <TextField
                        className="input-search"
                        style={{ marginLeft: '2px', marginRight: '2px' }}
                        placeholder={_t(`Search ${this.props.title.slice(0, this.props.title.indexOf(' '))}`)}
                        value={this.state.query}
                        onKeyDown={this.onKeyDown}
                        onChange={(_, newValue) => this.setState({ query: newValue || '' })}
                        onFocus={(e) => e.target.select()}
                        autoFocus
                    />
                    <div
                        className="odoo-muted-button search-icon"
                        style={{ border: 'none' }}
                        onClick={() => this.state.query.trim() && this.searchData(this.state.query)}>
                        <FontAwesomeIcon icon={faSearch} />
                    </div>
                </div>
            );
        }

        return (
            <div style={broadCampStyle}>
                {backButton}
                {searchButton}
                {refrechButton}
                {searchBar}
            </div>
        );
    }
}

SearchRefrech.contextType = AppContext;

export default SearchRefrech;
