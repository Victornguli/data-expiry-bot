## Internet Data Expiry Bot
Simple telegram bot for sending notifications before an internet data package expires, especially cases where the Telco data provider does not offer a non-reliquishable option of auto-renewing the subscription.

### Motivation:
Consider Telkom Kenya for example, on purchase of a 2GB daily package, when you rely on their auto renew approach all previous data will be reliquished and won't be carried forward to the next renewal. However if you decide to perform this task yourself before the previous package expires, then all unused data is carried foward and the expiry date is updated to reflect that of the most recent purchase.
Doing this manually to gain an "edge" over this practice, I often forgot and the data bundle expired before I could renew it. The margins for a long term purchase are also lower as compared to the daily renewals, I guess the Telcos know that we often forget to renew the packages in time :). 

#### How it works:
The solution is a simple bot utilising Telegram bot API that I can interact with and set a purchase date, as well as when to alert me(time) for my renewal. Further reminders are automatically calculated i.e if the previous purchase date was 10th August 2020 at 10:00PM then the bot will send out a reminder on 11th August 2020 at 9:00PM, an hour(this grace period can be customized too..) before the package expires.

#### Requirements
