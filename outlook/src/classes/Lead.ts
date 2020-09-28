class Lead {
    id: number;
    name: string;
    expectedRevenue: string; // string because formatted
    logged: boolean;

    static fromJSON(o: Object): Lead {
        var lead = new Lead();
        lead.id = o['id'];
        lead.name = o['name'];;
        lead.logged = o['logged'];

        let expectedRevenue = o['expected_revenue'];
        // Detects 00 decimals and remove them to make more space a reduce noise.
        if (expectedRevenue.search(/\.00\D*$/) != -1) { // if it ends with ".00" or ".00 $" or ".00 €", etc.
            expectedRevenue = expectedRevenue.replace(/\.00/, '');
        } else if (expectedRevenue.search(/,00\D*$/) != -1) { // if it ends with ",00" or ",00 $" or ",00 €", etc.
            expectedRevenue = expectedRevenue.replace(/,00/, '');
        }
        lead.expectedRevenue = expectedRevenue;

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