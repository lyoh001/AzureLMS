param location string = resourceGroup().location
param prefix string = replace(resourceGroup().name, 'rg', '')
// param prefix string = concat(replace(resourceGroup().name, 'rg', ''), substring(newGuid(), 0, 7))

resource storage_account 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  kind: 'StorageV2'
  location: location
  name: '${prefix}strg'
  properties: {
    accessTier: 'Hot'
  }
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
}
