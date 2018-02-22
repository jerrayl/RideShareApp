#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime
import webapp2
from google.appengine.ext import ndb

def full(ride):
    return len(ride.passengers)>=ride.capacity

class RideModel(ndb.Model):
    destination = ndb.StringProperty()
    date = ndb.DateProperty()
    time = ndb.TimeProperty()
    capacity = ndb.IntegerProperty()
    passengers = ndb.StringProperty(repeated = True)
    origin = ndb.StringProperty()
    
class CreateRide(webapp2.RequestHandler):
    def post(self):
        ride = RideModel()
        ride.destination = self.request.get('destination')
        date = self.request.get('date').split("/")
        ride.date = datetime.date(int(date[2]),int(date[1]),int(date[0]))
        ride.time = datetime.time(int(self.request.get('time')[0:2]),int(self.request.get('time')[2:]))
        ride.capacity = int(self.request.get('capacity'))
        ride.origin = self.request.get('origin')
        ride.passengers = [self.request.get('passengers')]
        ride.put()

class AddToRide(webapp2.RequestHandler):
    def post(self):
        ride = ndb.Key('RideModel', int(self.request.get('key'))).get()
        if self.request.get('name') not in ride.passengers:
            ride.passengers += [self.request.get('name')]
            ride.put()
        
class GetRides(webapp2.RequestHandler):
    def get(self):
        rides = RideModel.query().fetch()
        self.response.write(rides)

class GetSelectedRides(webapp2.RequestHandler):
    def get(self):
        date = self.request.get('date').split("/")
        if self.request.get('destination') == "All" and self.request.get('origin') == "All":
            rides = RideModel.query(RideModel.date == datetime.date(int(date[2]),int(date[1]),int(date[0]))).fetch()
        elif self.request.get('destination') == "All":
            rides = RideModel.query(ndb.AND(RideModel.origin == self.request.get('origin'), RideModel.date == datetime.date(int(date[2]),int(date[1]),int(date[0])))).fetch()
        elif self.request.get('origin') == "All":
            rides = RideModel.query(ndb.AND(RideModel.destination == self.request.get('destination'), RideModel.date == datetime.date(int(date[2]),int(date[1]),int(date[0])))).fetch()
        else:
            rides = RideModel.query(ndb.AND(RideModel.origin == self.request.get('origin'), RideModel.destination == self.request.get('destination'), RideModel.date == datetime.date(int(date[2]),int(date[1]),int(date[0])))).fetch()
        self.response.write([[str(ride.key.integer_id()), str(ride.origin) + "->" + str(ride.destination) + " " + datetime.date.strftime(ride.date,"%d/%m/%y") +" " + datetime.time.strftime(ride.time,"%I:%m%p")] for ride in rides if not full(ride)])

class GetUserRides(webapp2.RequestHandler):
    def get(self):
        rides = RideModel.query(ndb.AND(RideModel.passengers == self.request.get('name'), RideModel.date >= datetime.date.today())).fetch()
        self.response.write([[str(ride.key.integer_id()), str(ride.origin) + "->" + str(ride.destination) + " " + datetime.date.strftime(ride.date,"%d/%m/%y") +" " + datetime.time.strftime(ride.time,"%I:%m%p")] for ride in rides])

class GetTodayRides(webapp2.RequestHandler):
    def get(self):
        rides = RideModel.query(RideModel.date == datetime.date.today()).fetch()
        self.response.write([[str(ride.key.integer_id()), str(ride.origin) + "->" + str(ride.destination) + " " + datetime.time.strftime(ride.time,"%I:%M%p")] for ride in rides if not full(ride)])

class GetRide(webapp2.RequestHandler):
    def get(self):
        ride = ndb.Key('RideModel', int(self.request.get('key'))).get()
        self.response.write([str(ride.origin),str(ride.destination),datetime.date.strftime(ride.date,"%d/%m/%y"),datetime.time.strftime(ride.time,"%I:%m%p"),ride.capacity,[str(p) for p in ride.passengers]])

app = webapp2.WSGIApplication([
    ('/create', CreateRide),
    ('/add', AddToRide),
    ('/getall', GetRides),
    ('/getselected', GetSelectedRides),
    ('/getuser', GetUserRides),
    ('/gettoday', GetTodayRides),
    ('/getride', GetRide)
], debug=True)
