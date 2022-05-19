# VICGOV - Azure LMS
## 1. Introduction
### 1.1	Overview

A Script runs from on-prem server every weekday at 8:15AM, to get the LMS Data attachment from the mailbox. The script connects to the mailbox using service account, however the script fails at the "extract the attachment process".

The script has been running fine for years and recently the exchange connection attempt fails.

This document is intended to provide a high level overview of workflow on how the automation transfers attachment files from the mailbox to onprem server and notifies the admins with job status alert email.

Included a step by step detailed analysis notebook around identifying the root cause of the script to fail. (ref: https://github.com/lyoh001/AzureLMS/blob/main/analysis/analysis_eda.ipynb)


![Figure 1: Powerbi Dashboard](./.images/dashboard.png)
(ref: https://github.com/lyoh001/AzureLMS/blob/main/analysis/powerbi_dashboard.pdf)

## 2 LMS Integration Process Reports
- Description: Fetching outlook mail attachment from the mailbox and copy them to the on-prem server..
- Priority: 3
- Owners: Tier 0

## 3 Logical Architecture
### 3.1	Logical System Component Overview
![Figure 1: Logical Architecture Overview](./.images/workflow.png)
1. At 8:15am, logic app gets triggered by a scheduler, this is an intended design to due to the fact that WEBSITE_TIME_ZONE is not currently supported on Azure Linux Consumption plan. (ref: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-python)
1. A function gets invoked via logicapp. 
1. The function will auth via managed identity against Azure AD and retrieves API credentials from Azure Keyvault that is secured under T0 subscription.
1. SPN has permission to retrieve an attachment from a given mailbox.
1. The function will then retrieve the attachment from the mailbox and save it to a storage account.
1. The Logicapp will invoke an automation account runbook via a webhook HTTP post call.
1. Azure Arc Hybridworker will excute a powershell and mount a storage on on-prem server.
1. Powershell will then copy the file from the storage account to the mounted drive via Azcopy.
1. Logic app will send the end user a notification of workflow status.

## Used By

This project is used by the following teams:

- OD Learning
- Cloud Platform