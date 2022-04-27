import './ListItem.css';
import * as React from 'react';
import Logger from '../Log/Logger';
import api from '../../api';
import AppContext from '../AppContext';

type ListItemProps = {
    title: string;
    description?: string;
    // Record information to redirect to Odoo
    // and log email on the record
    model: string;
    res_id: number;
    logTitle: string;
};

class ListItem extends React.Component<ListItemProps, {}> {
    openInOdoo = () => {
        const cids = this.context.getUserCompaniesString();
        const url = `${api.baseURL}/web#id=${this.props.res_id}&model=${this.props.model}&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    render() {
        return (
            <div className="list-item-root-container" onClick={this.openInOdoo}>
                <div className="list-item-container">
                    <div className="list-item-info-container">
                        <div className="list-item-title-text">{this.props.title}</div>
                        {this.props.description && (
                            <div className="list-item-description">{this.props.description}</div>
                        )}
                    </div>
                    <Logger resId={this.props.res_id} model={this.props.model} tooltipContent={this.props.logTitle} />
                </div>
            </div>
        );
    }
}

ListItem.contextType = AppContext;

export default ListItem;
