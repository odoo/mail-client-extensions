#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -d odoo.com/subdomain"
   echo -e "\t-d The domain that will replace localhost:3000 in the manifest.xml and api.js files."
   exit 1 # Exit script after printing help
}

while getopts "d:" opt
do
   case "$opt" in
      d ) parameterD="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$parameterD" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

escapedD=$(echo "$parameterD" | sed 's/\//\\\//g')
sed -i "s/localhost:3000/$escapedD/" dist/manifest.xml
sed -i "s/localhost:3000/$escapedD/" dist/taskpane.js