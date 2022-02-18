# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 11:14:53 2022

@author: U54979
"""

#pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org garminconnect
#pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fitdecode
#pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org auto-py-to-exe
#

#import logging
import datetime

from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

# Configure debug logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

# Example dates
today = datetime.date.today()
lastweek = today - datetime.timedelta(days=7)

#try:
    # API

    ## Initialize Garmin api with your credentials
api = Garmin("julianlatasa@gmail.com", "Julian80")

    ## Login to Garmin Connect portal
api.login()
    
    # ACTIVITIES

    # Get activities data from start and limit
    #activities = api.get_activities(0,1) # 0=start, 1=limit
#    logger.info(activities)

    # Get activities data from startdate 'YYYY-MM-DD' to enddate 'YYYY-MM-DD', with (optional) activitytype
    # Possible values are [cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other]
activities = api.get_activities_by_date('2021-11-01', '2022-01-24', 'swimming')

    # Get last activity
    #logger.info(api.get_last_activity())

    ## Download an Activity
for activity in activities:
    activity_id = activity["activityId"]
##        logger.info("api.download_activities(%s)", activity_id)

#    gpx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.GPX)
#    output_file = f"./{str(activity_id)}.gpx"
#    with open(output_file, "wb") as fb:
#        fb.write(gpx_data)

#    tcx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.TCX)
#    output_file = f"./{str(activity_id)}.tcx"
#    with open(output_file, "wb") as fb:
#        fb.write(tcx_data)

    zip_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
    output_file = f"./{str(activity_id)}.zip"
    with open(output_file, "wb") as fb:
        fb.write(zip_data)

#    csv_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.CSV)
#    output_file = f"./{str(activity_id)}.csv"
#    with open(output_file, "wb") as fb:
#         fb.write(csv_data)

    ## Get activity splits
#first_activity_id = activities[0].get("activityId")
#owner_display_name =  activities[0].get("ownerDisplayName")

#    logger.info(api.get_activity_splits(first_activity_id))

    ## Get activity split summaries for activity id
#    logger.info(api.get_activity_split_summaries(first_activity_id))

    ## Get activity weather data for activity
#    logger.info(api.get_activity_weather(first_activity_id))

    ## Get activity hr timezones id
#    logger.info(api.get_activity_hr_in_timezones(first_activity_id))

    ## Get activity details for activity id
#    logger.info(api.get_activity_details(first_activity_id))

    # ## Get gear data for activity id
#    logger.info(api.get_activity_gear(first_activity_id))

    ## Activity self evaluation data for activity id
#    logger.info(api.get_activity_evaluation(first_activity_id))

    ## Logout of Garmin Connect portal
    # api.logout()

#except (
#        GarminConnectConnectionError,
#        GarminConnectAuthenticationError,
#        GarminConnectTooManyRequestsError,
#    ) as err:
#    logger.error("Error occurred during Garmin Connect communication: %s", err)
