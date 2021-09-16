import * as React from 'react';
import Partner from '../../../../classes/Partner';

import ContactListItem from '../ContactList/ContactListItem/ContactListItem';

import api from '../../../api';
import AppContext from '../../AppContext';

type ContactSectionProps = {
    partner: Partner;
    onPartnerInfoChanged?: (partner: Partner) => void;
};

class ContactSection extends React.Component<ContactSectionProps, {}> {
    viewContact = (partner) => {
        const cids = this.context.getUserCompaniesString();
        let url = api.baseURL + `/web#id=${partner.id}&model=res.partner&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    render() {
        let selectable = this.props.partner.isAddedToDatabase();
        let onItemClick = this.props.partner.isAddedToDatabase() ? this.viewContact : undefined;

        return (
            <div className="section-card">
                <ContactListItem partner={this.props.partner} selectable={selectable} onItemClick={onItemClick} />
            </div>
        );
    }
}
ContactSection.contextType = AppContext;

export default ContactSection;
