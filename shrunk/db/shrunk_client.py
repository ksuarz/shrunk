""" shrunk - Rutgers University URL Shortener

Implements database-level interactions for the shrunk application.
"""
import datetime
import random
import string

import pymongo


class ShrunkClient(object):
    """A class for database interactions."""

    def __init__(self, host=None, port=None):
        """
        Create a new client connection.

        This client uses MongoDB. No network traffic occurs until a data method
        is called.

        :Parameters:
          - `host` (optional): the hostname to connect to; defaults to
            "localhost"
          - `port` (optional): the port to connect to on the server; defaults to
            the database default if not present
        """
        self._mongo = pymongo.MongoClient(host, port)

    def create_short_url(self, long_url, netid=None):
        """Given a long URL, create a new short URL.
        
        Randomly creates a new short URL and updates the Shrunk database.

        :Parameters:
          - `long_url`: The original URL to shrink.
          - `netid` (optional): The creator of this URL.

        :Returns:
          The shortened URL, or None if an error occurs.
        """
        short_url  = ShrunkClient._generate_unique_key()
        db = self._mongo.shrunk_urls

        # Update MongoDB
        db.urls.insert({
            "_id" : short_url,
            "url" : long_url,
            "netid" : netid,
            "timeCreated" : datetime.datetime.now(),
            "visits" : 0
        })
        return short_url

    def delete_url(self, short_url):
        """Given a short URL, delete it from the database.

        This deletes all information associated with the short URL and wipes all
        appropriate databases.
        
        :Parameters:
          - `short_url`: The shortened URL to dete.

        :Returns:
          A response in JSON detailing the effect of the database operations.
        """
        url_db = self._mongo.shrunk_urls
        visit_db = self._mongo.shrunk_visits
        if short_url is None:
            return {
                "urlDataResponse" : {"nRemoved" : 0},
                "visitDataResponse" : {"nRemoved" : 0}
            }
        else:
            return {
                "urlDataResponse" : url_db.urls.remove({
                    "_id" : short_url
                }),
                "visitDataResponse" : visit_db.visits.remove({
                    "url" : short_url
                })
            }

    def delete_user_urls(self, netid):
        """Deletes all URLs associated with a given NetID.

        The response, encoded as a JSON-compatible Python dict, will at least
        contained an "nRemoved" indicating the number of records removed.

        :Parameters:
          - `netid`: The NetID of the URLs to delete.
        
        :Returns:
          A response in JSON detailing the effect of the database operations.
        """
        db = self.mongo.shrunk_urls
        if netid is None:
            return {"nRemoved" : 0}
        else:
            return db.urls.remove({"netid" : netid})

    def get_url_info(self, short_url):
        """Given a short URL, return information about it.

        This returns a dictionary containing the following fields:
          - url : The original unshrunk URL
          - timeCreated: The time the URL was created, expressed as an ISODate
            instance
          - netid : If it exists, the creator of the shortened URL
          - visits : The number of visits to this URL

        :Parameters:
          - `short_url`: A shortened URL
        """
        db = self._mongo.shrunk_urls
        return db.urls.find_one({"_id" : short_url})

    def get_long_url(self, short_url):
        """Given a short URL, returns the long URL.
        
        :Parameters:
          - `short_url`: A shortened URL
        
        :Returns:
          The long URL, or None if the short URL does not exist.
        """
        result = self.get_url_info(short_url)
        if result is not None:
            return result["url"]
        else:
            return None

    def get_visits(self, short_url):
        """Returns all visit information to the given short URL.
        
        :Parameters:
          - `short_url`: A shortened URL

        :Response:
          - A JSON-compatible Python dict containing the database response.
        """
        db = self._mongo.shrunk_visits
        return db.visits.find({"short_url" : short_url})

    def get_num_visits(self, short_url):
        """Given a short URL, return the number of visits.
        
        :Parameters:
          - `short_url`: A shortened URL

        :Returns:
          A nonnegative integer indicating the number of times the URL has been
          visited, or None if the URL does not exist in the database.
        """
        db = self._mongo.shrunk_urls
        try:
            # Can be at most one document
            [document] = [doc for doc in db.urls.find({"_id" : short_url})]
            return document["visits"]
        except ValueError:
            # There were no values to unpack
            return None

    def get_urls(self, netid):
        """Gets all the URLs created by the given NetID.
        
        :Parameters:
          - `netid`: A Rutgers NetID

        :Returns:
          A JSON-compatible Python dict containing a list of URLs.
        """
        db = self._mongo.shrunk_urls
        return db.urls.find({"netid" : netid})

    def visit(self, short_url, source_ip):
        """Visits the given URL and logs visit information.
        
        On visiting a URL, this is guaranteed to perform at least the following
        side effects if the URL is valid:
          - Increment the hit counter
          - Log the visitor

        If the URL is invalid, no side effects will occur.

        :Returns:
          The long URL corresponding to the short URL, or None if no such URL
          was found in the database.
        """
        db = self._mongo.shrunk_urls
        # TODO return type and validation that the URL exists
        db.urls.update({"_id" : short_url},
                       {"$inc" : {"visits" : 1}})

        # TODO Do we need the source ip or can we detect it?
        db = self._mongo.shrunk_visits
        db.visits.insert({
            "url" : short_url,
            "source_ip" : source_ip,
            "time" : datetime.datetime.now()
        })

    @staticmethod
    def _generate_unique_key():
        """Generates a unique key in the database."""
        # TODO
        length = random.choice(range(5, 10))
        return "".join(
                random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(length))
