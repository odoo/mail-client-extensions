import * as React from "react";
import {ProfileCard, ProfileCardProps} from "../ProfileCard/ProfileCard";
import AppContext from '../AppContext';
import { HttpVerb, sendHttpRequest, ContentType } from "../../../utils/httpRequest";
import api from "../../api";

type ContactProps = {};
type ContactState = {};

class Contact extends React.Component<ContactProps, ContactState> {
    constructor(props, context) {
        super(props, context);
    }

  addToContacts = () => {
    const requestJson = {
        name: this.context.partner.name,
        email: this.context.partner.email,
        company: this.context.partner.company.id
    }
    const cancellableRequest = sendHttpRequest(HttpVerb.POST, api.baseURL + api.contactCreate, ContentType.Json, this.context.getConnectionToken(), requestJson, true)
    this.context.addRequestCanceller(cancellableRequest.cancel);
    cancellableRequest.promise.then((response) => {
        console.log(response);
        const parsed = JSON.parse(response);
        this.context.setPartnerId(parsed.result.id)
        }).catch(function(error) {
        console.log("Error catched: " + error);
        })
    }
  
  render() {
    const profileCardData: ProfileCardProps = {
        domain: undefined,
        name: this.context.partner.name,
        initials: this.context.partner.getInitials(),
        icon: this.context.partner.image ? "data:image;base64, " + this.context.partner.image : undefined,
        job: this.context.partner.title,
        phone: this.context.partner.mobile || this.context.partner.phone,
        twitter: undefined,
        facebook: undefined,
        crunchbase: undefined,
        linkedin: undefined,
        description: undefined
    }

    // The add button next to Contact should always appear when disconnected, to redirect to the login page.
    // This button should not appear if the partner already has an id (which means it was added already).
    // It should not appear either if the company could not be created.
    return <React.Fragment>
        <div className='tile-title-space'>
            <div className='tile-title'>
                <div className='text'>CONTACT DETAILS</div>
                {!this.context.isConnected() || this.context.partner.id === -1 ? <div className='button' onClick={this.context.isConnected() ? this.addToContacts : this.context.navigation.goToLogin}>Add</div> : null}
            </div>
        </div>
        
        <ProfileCard {...profileCardData} />
      </React.Fragment>;
  }
}
Contact.contextType = AppContext;
export default Contact;
