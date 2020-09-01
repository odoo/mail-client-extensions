import * as React from 'react';
import LeadData from "../../../../classes/Lead";
import api from "../../../api";
import AppContext from '../../AppContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCheck, faReply } from '@fortawesome/free-solid-svg-icons'

import './LeadList.css';


type LeadListProps = {
    leads: LeadData[];
    showMore: boolean;
    more: () => void;
    log: (leadId: number) => void;
};
type LeadListState = {};

class LeadListCompact extends React.Component<LeadListProps, LeadListState> {
    constructor(props) {
        super(props);
        this.state = { };
    }

    private _leadClick = (leadId: number) => {
        window.open(api.baseURL + "/web#action=crm.crm_lead_action_pipeline&view_type=form&id=" + leadId,"_blank")
    }

    public render(): JSX.Element {
        const leadElements = [];
        for (const lead of this.props.leads) {
            leadElements.push(<div className='opportunity'>
                <div className='body' onClick={()=>this._leadClick(lead.id)}>
                    <div className='title'>{lead.name}</div>
                    <div className='price'>{lead.expectedRevenue}</div>
                </div>
        
                <div className='logicon' onClick={() => {this.props.log(lead.id)}}>
                    {lead.logged ? <FontAwesomeIcon icon={faCheck}/> : <FontAwesomeIcon icon={faReply} flip='horizontal'/>}
                </div>
            </div>)
        }
        return (
            <>
                {leadElements}
                {this.props.showMore ? <div className='link-like-button' onClick={() => this.props.more()}>Load more</div> : null}
            </>
        );
    }
}
export default LeadListCompact;
LeadListCompact.contextType = AppContext;