class Lead {
    id: number;
    name: string;
    expectedRevenue: string; // string because formatted
    logged: boolean;

    static fromJSON(o: Object): Lead {
        var lead = new Lead();
        lead.id = o['id'];
        lead.name = o['name'];
        lead.expectedRevenue = o['expected_revenue'];
        lead.logged = o['logged'];
        return lead;
    }

    static copy(lead: Lead): Lead {
        const newLead = new Lead();
        newLead.id = lead.id;
        newLead.name = lead.name;
        newLead.expectedRevenue = lead.expectedRevenue;
        newLead.logged = lead.logged;
        return newLead;
    }
}

export default Lead;