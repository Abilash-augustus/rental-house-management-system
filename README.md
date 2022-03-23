
# RENTAL HOUSE MANAGEMENT SYSTEM
[![GitHub license](https://img.shields.io/github/license/shumwe/rental-house-management-system)](https://github.com/shumwe/rental-house-management-system)
[![GitHub issues](https://img.shields.io/github/issues/shumwe/rental-house-management-system)](https://github.com/shumwe/rental-house-management-system/issues)
[![GitHub forks](https://img.shields.io/github/forks/shumwe/rental-house-management-system)](https://github.com/shumwe/rental-house-management-system/network)
[![GitHub stars](https://img.shields.io/github/stars/shumwe/rental-house-management-system)](https://github.com/shumwe/rental-house-management-system/stargazers)

RHMS is a web-based application developed using the _Django framework_. The aim is to help tenants and rental house managers track 
rental arears and utility(water and electricity) payments while at the same time providing a communication chain, manager &harr; tenants
that is free from disruptions. Both parties are able to view and visualize previous payments and consumption details (for electricity and water)
at any particular time.


**Currently included functionalities for the managers**
```

- [x] Utility (Electricity & Water) Tracking and Management
- [x] Payments Management
- [x] Adding Rental Houses
- [x] Managed building upkeep (includes adding rental units, updating status e.t.c)
- [x] Add Managers
- [x] Tenant Management
- [x] Hired Personnel Management
- [x] Work Order Management
- [x] Reports, complaints and Maintenance Management (includes creating notices with pdf print option)
- [X] Visits Scheduling and Management 
- [X] Communications and Notifications Management (powered by sendgrid)
- [x] Eviction Management
- [x] Managing Move Out Notices
```
**Currently included tenants' functionalities**
```

- [x] Personal Rent and utility tracking (visualizing electricity & water consumtion)
- [ ] Online payments submission (MPESA Integration & stripe :white_check_mark )
- [x] View payments history
- [x] Keep track of notices nade by managers
- [x] View receieved notices & create moveout notice
- [x] View and send tenancy related emails using the platform
- [x] Make Complaints
- [x] Create house reports
- [x] Submit service rating (30 days from preveous rating)
```
**Shared Funtionalities**
```
- [x] Account Management
    - SignUp & login, password change/reset, email confiration, profile update
- [x] Online messaging (Telegram BOT)
- [x] Contact
- [x] Scheduling visits
- [x] Searching with django filters 
```

## Modules


- [Accounts](https://github.com/shumwe/rental-house-management-system/tree/main/accounts)
    - User
    - Profiles
    - Managers
    - Tenants

- [Core](https://github.com/shumwe/rental-house-management-system/tree/main/core)
    - Contact
        - Contacts Reply
    - Unit Tour | Visits
    - Move OutNotice
    - Eviction Notice
    - Service rating
    - Communications & Emails

- [Complaints & Reports ](https://github.com/shumwe/rental-house-management-system/tree/main/complaints)
    - Unit Report Type
    - Unit Report
    - Unit Report Album
    - Complaints
    - Help Contacts

- [Rental Property](https://github.com/shumwe/rental-house-management-system/tree/main/rental_property)
    - Counties
        - Estate
        - Building
            - Unit Type
            - Rental Unit
                - Unit Album
            - MaintananceNotice

- [Utilities & Rent](https://github.com/shumwe/rental-house-management-system/tree/main/utilities)
    - Payment Methods
    - Unit Rent Details
        - Rent Payment
    - Water Billing
        - Water Consumption (Radings)
        - Water Payments
    - Electricity Billing
        - Electricity Reading (Consumption)
        - Electricity Payments
    - Water Meter
    - Electricity Meter

- [Work Order](https://github.com/shumwe/rental-house-management-system/tree/main/work_order)
    - Hired Personnel
        - Personnel Contact
    - Work Order
        - WorkOrderPayments

- [Reporting](https://github.com/shumwe/rental-house-management-system/tree/main/reporting)
    - ** Reports