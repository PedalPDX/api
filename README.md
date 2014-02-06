PedalAPI
========

from flask import Flask, jsonify, make_response, request
from random import randint
from os import listdir
import json
from markdown2 import markdown

| Command                                           | Result                                               |
| :--------                                         | :-------                                             |
| GET server.address.com:5000/                      | Returns this README                                  |
| GET server.address.com:5000/pedal/0.3/rides       | Returns all know ride ID's                           |
| GET server.address.com:5000/pedal/0.3/rides/<ID>  | Returns information on the specified id              |
| GET server.address.com:5000/pedal/0.3/rides/newID | Returns a random ID to be used to upload a new ride  |
| POST server.address.com:5000/pedal/0.3/rides      | Used for uploading ride information including ID     |
| POST server.address.com:5000/pedal/0.3/rides/<ID> | Used for uploading ride information to a specific ID |


