# VICGOV - Azure LMS

## Table of Contents
1. [Introduction](#1-introduction)
   1. [Overview](#11-overview)
2. [LMS Integration Process Reports](#2-lms-integration-process-reports)
3. [Logical Architecture](#3-logical-architecture)
   1. [Logical System Component Overview](#31-logical-system-component-overview)
4. [Used By](#4-used-by)

## 1. Introduction
### 1.1 Overview

The VICGOV - Azure LMS is a script that runs from an on-prem server every weekday at 8:15AM to fetch the LMS Data attachment from a mailbox. The script connects to the mailbox using a service account; however, it currently fails at the "extract the attachment process" step.

This document provides a high-level overview of the workflow, describing how the automation transfers attachment files from the mailbox to the on-prem server and notifies the admins with a job status alert email.

A step-by-step detailed analysis notebook is available to help identify the root cause of the script failure. You can find the notebook [here](https://github.com/lyoh001/AzureLMS/blob/main/analysis/analysis_eda.ipynb).

## 2. LMS Integration Process Reports
- **Description**: Fetching Outlook mail attachments from the mailbox and copying them to the on-prem server.
- **Priority**: 3
- **Owners**: Tier 0

## 3. Logical Architecture
### 3.1 Logical System Component Overview
![Figure 1: Logical Architecture Overview](./.images/workflow.png)

The logical architecture of the VICGOV - Azure LMS is as follows:

1. At 8:15am, a logic app is triggered by a scheduler. This design is intentional due to the lack of support for WEBSITE_TIME_ZONE on the Azure Linux Consumption plan. (Reference: [Azure Functions Timer Trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=in-process&pivots=programming-language-python))
2. A function gets invoked via the logic app.
3. The function authenticates via managed identity against Azure AD and retrieves API credentials from Azure Key Vault secured under the T0 subscription.
4. The service principal has permission to retrieve an attachment from a given mailbox.
5. The function retrieves the attachment from the mailbox and saves it to a storage account.
6. The logic app invokes an automation account runbook via a webhook HTTP POST call.
7. Azure Arc Hybrid Worker executes a PowerShell script and mounts a storage on the on-prem server.
8. PowerShell copies the file from the storage account to the mounted drive using Azcopy.
9. The logic app sends the end user a notification of the workflow status.

## 4. Used By

This project is used by the following teams:

- OD Learning
- Cloud Platform
