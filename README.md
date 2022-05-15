# VICGOV - Azure LMS
## 1. Introduction
### 1.1	Overview

A number of challenges arise when managing AAD roles across multiple tenants, Hosting Services team have been working to make this process easier to maintain with less administrative overhead.

This document is intended to provide a high level overview of workflow on how the automation transfers files from Gofex SFT client to Sharepoint dir https://****.sharepoint.com/sites/****/****/Technical Documents/GoFex Reporting and notifies the admins with job status alert email.

Included in this report is a step by step detailed guide around where to look for troubleshooting.

## 2 Go Fex Sharepoint Integration Process Reports
- Description: MS Sharepoint integration from the on-prem server..
- Priority: 3
- Owners: Tier 0

## 3 Logical Architecture
### 3.1	Logical System Component Overview
![Figure 1: Logical Architecture Overview](./.images/workflow.png)
1. At 8am Mon~Fri, logic app gets triggered by a scheduler, this is an intended design to due to the fact that WEBSITE_TIME_ZONE is not currently supported on Azure Linux Consumption plan. (ref: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-python)
1. A function gets invoked via logicapp. 
1. The function will auth via managed identity against Azure AD and retrieves API credentials from Azure Keyvault that is secured under T0 subscription.
1. SPN has permission to retrieve an attachment from a given mailbox.
1. The function will then retrieve the attachment from the mailbox and save it to a storage account.
1. The function will invoke an automation account runbook via a webhook post call.
1. Hybridworker will excute a powershell and mount a storage on on-prem server.
1. Powershell will then copy the file from the storage account to the mounted drive via Azcopy.
1. Logic app will send the end user a notification of workflow status.

## Used By

This project is used by the following teams:

- BAS
- Cloud Platform