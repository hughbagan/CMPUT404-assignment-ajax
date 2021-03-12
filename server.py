#!/usr/bin/env python
# coding: utf-8
# Copyright 2021 Abram Hindle, Hugh Bagan
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
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, Response
import json
app = Flask(__name__)
app.debug = True

# An example world
# { <-- self.space
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()

    def clear(self):
        self.space = dict()
        
    def update(self, entity, key, value):
        # updates a value of an existing entity, 
        # or creates a new one if it doesn't exist
        # NOTE: it won't stop the use of erroneous keys other than 'x' or 'y'
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        # assign an entity to a dictionary of entries
        # an entity has a name
        self.space[entity] = data

    def get(self, entity):
        # returns an entity, or empty dict if entity is not found
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
       # ^ wtf does that mean?
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])


@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect("/static/index.html")


@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    print(request.data)
    # get_json() returns dict on success and None on failure.
    # free_tests.py passes in bytes, so I'm going to ignore mimetype
    data = request.get_json(force=True)
    print(data)
    # entity is the <str> path ending; the name of the entity
    create_mode = myWorld.get(entity) == dict()
    print("create_mode", create_mode)
    if request.method=='POST':
        for key in data:
            try:
                myWorld.update(entity, key, data[key])
            except Exception as e:
                return Response(str(e), status=500)
    elif request.method=='PUT':
        try:
            myWorld.set(entity, data)
        except Exception as e:
            return Response(str(e), status=500)
        return json.dumps(myWorld.get(entity)) # "returns the obj that was PUT"
    else:
        print(request.method)
        return Response(status=405) # Method Not Allowed
    if create_mode:
        return Response(status=201) # Created
    else:
        return Response(status=204) # No Content


@app.route("/entity/<entity>", methods=['GET']) # (method was not specified)
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    # need to convert from JSON to dict?
    return json.dumps(myWorld.get(entity))


@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    if request.method=='GET' or request.method=='POST': # if GET, return world as JSON
        return json.dumps(myWorld.world())
    else: # what about POST ?
        print(request.method)
        return Response(status=405) # Method Not Allowed


@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    world_state = myWorld.world()
    return json.dumps(world_state) # /clear returns the state of the world {}
                                   # TODO: before or after we clear it???


if __name__ == "__main__":
    app.run()
