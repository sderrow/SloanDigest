# SloanDigest

SloanDigest is an Alexa Flash Briefing Skill to help make MIT Sloan students' lives easier. It aggregates information relating to upcoming events (from SloanGroups), key academic dates (from MIT), and "Meet a Sloanie" profiles from user submissions. SloanDigest is fully automated and can pull updated information at regular intervals (e.g., daily).

SloanDigest reads the briefing from a [JSON feed](https://s3.amazonaws.com/sloandigest/SloanDigest.json) hosted on an AWS S3 bucket.

The publishing script is written in Python and lives in AWS Lambda. The script scrapes fresh data from its various inputs (see below) and publishes to the JSON file above.

## Data Sources:
SloanGroups currently only has a credentialed  endpoint for downloading event information. As a temporary workaround, we took a snapshot of this JSON endpoint and uploaded the [copy to an S3 bucket](https://s3.amazonaws.com/sloandigest/sloangroups.json).  
The key academic dates Google Sheet may be found [here](https://docs.google.com/spreadsheets/d/1z1A4DQRTGwE4rzh5bpNXC85J8XPs3ZsWHVOgu_C-Ioo/edit?usp=sharing).  
The "Meet a Sloanie" Google Form is [here](https://goo.gl/forms/MQ2MDhYWZIhaa0rM2).  
The "Meet a Sloanie" results are available [here](https://docs.google.com/spreadsheets/d/1G6oJTyR7NVjN79JgW2Qf7cs2U7-EGkBL-e3LNW--hZE/edit?usp=sharing).
