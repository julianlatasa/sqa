# -*- coding: utf-8 -*-
"""Python 3 API wrapper for Garmin Connect to get your statistics."""
import logging
logger = logging.getLogger(__name__)

import garminconnect

import datetime

class mytimedelta(datetime.timedelta):
   def __str__(self):
      seconds = self.total_seconds()
      hours = seconds // 3600
      minutes = (seconds % 3600) // 60
      seconds = seconds % 60
      str = '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))
      return (str)

class Garmin(garminconnect.Garmin):
    """Class for fetching data from Garmin Connect."""

    def get_connections_count(self):  #
        """Fetch available heart rates data 'cDate' format 'YYYY-mm-dd'."""
        self.garmin_connect_connections_count_url = "proxy/connection-service/connection/connections/count"

        url = f"{self.garmin_connect_connections_count_url}"
        logger.debug("Requesting connections count")

        return self.modern_rest_client.get(url).json()


    def get_connections(self):  #
        """Fetch available heart rates data 'cDate' format 'YYYY-mm-dd'."""
        self.garmin_connect_connections_url = (
            "proxy/connection-service/connection/connections/pagination"
        )

        url = f"{self.garmin_connect_connections_url}/{self.display_name}"
        params = {
            "start": str(1),
            "limit": str(self.get_connections_count()),
        }
        logger.debug("Requesting connections")

        return self.modern_rest_client.get(url, params=params).json()

    def get_connection_activities(self, connection_display_name, start, limit):
        """Return available activities."""
        self.garmin_connect_connection_activities = (
            "proxy/activitylist-service/activities"
        )

        url = f"{self.garmin_connect_connection_activities}/{connection_display_name}"
        params = {"start": str(start), "limit": str(limit)}
        logger.debug("Requesting activities for connection")

        return self.modern_rest_client.get(url, params=params).json()





