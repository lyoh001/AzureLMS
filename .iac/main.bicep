targetScope = 'subscription'
@secure()
param token string
@secure()
param password string

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${deployment().name}rg'
  location: deployment().location
}

module automationaccount 'automationaccount.bicep' = {
  name: 'automationaccount'
  scope: rg
}

module funcapp 'funcapp.bicep' = {
  name: 'funcapp'
  scope: rg
}

module logicapps 'logicapps.bicep' = {
  name: 'logicapps'
  scope: rg
}

module storage 'storage.bicep' = {
  name: 'storage'
  scope: rg
}
