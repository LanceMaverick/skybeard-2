# National Rail Plugin v1.0 for Skybeard 2

First beta release of the National Rail Live Departures plugin for Skybeard v2. 
## Getting Departures from Any UK Station
To obtain lives departures from a specific national rail station use the `departures` command within Skybeard. The current version allows the user to search via exact stationf name or station code as defined on the National Rail website (generic search terms are in development). For example for departures from Roche:

`/departures Roche`

 `/departures ROC`

furthermore the search can be narrowed to services stopping a specific calling point:

`/departures Roche to Par`

it should be noted however that due to the constraints of message size within Telegram, stations with a large number of listed departures may cause issues. This will be addressed in later builds.

## Checking TOC Statuses
The status of all main Train Operating Companies can be obtained using the `/status` command.

## Checking Service Disruptions
A list of service disruptions for the current day can be displayed with the added option of specifying a keyword for the required TOC:

`/disruptions`

`/disruptions [TOC]`
