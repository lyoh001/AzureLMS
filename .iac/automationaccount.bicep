param location string = resourceGroup().location
param prefix string = replace(resourceGroup().name, 'rg', '')
// param prefix string = concat(replace(resourceGroup().name, 'rg', ''), substring(newGuid(), 0, 7))

resource automation_account 'Microsoft.Automation/automationAccounts@2015-10-31' = {
  location: location
  name: '${prefix}aa'
  properties: {
    sku: {
      name: 'Basic'
    }
  }
}
