PedalAPI
========

Depends
-------
* Flask
* Markdown
* psycopg2
* simplekml

About the API
-------------
This API is for use by the [PedalPDXApplication](http://pedal.cs.pdx.edu) bicycle route tracking application.

<iframe width="640" height="530" src="//www.youtube.com/embed/Hzo3JjxoVak/?rel=0" rel="0" frameborder="0" allowfullscreen></iframe>

Commands
--------

| Type  | Command                          | Result                                           |
| :---- | :------------------------------- | :----------------------------------------------- |
| GET   | api.pedal.cs.pdx.edu/            | Returns this README                              |
| GET   | api.pedal.cs.pdx.edu/version     | Returns the current version of the PedalAPI      |
| GET   | api.pedal.cs.pdx.edu/rides       | Returns all know ride ID's                       |
| GET   | api.pedal.cs.pdx.edu/rides/{ID}  | Returns information on the specified id          |
| GET   | api.pedal.cs.pdx.edu/kml/{ID}    | Returns a KML file of the ride                   |
| GET   | api.pedal.cs.pdx.edu/map/{ID}    | Redirects you to Google maps to view the ride    |
| GET   | api.pedal.cs.pdx.edu/latest      | Returns the last ten rides added to the api      |
| GET   | api.pedal.cs.pdx.edu/all         | Returns KML file containing every ride in the DB |
| POST  | api.pedal.cs.pdx.edu/rides       | Used for uploading ride information              |
| POST  | api.pedal.cs.pdx.edu/kml         | Uses form data to construct a kml file           |

Examples
--------

To Return This README:

`curl -i -X GET api.pedal.cs.pdx.edu`

To return all stored data pertaining to the ride under the ID 874323:

`curl -i -X GET api.pedal.cs.pdx.edu/rides/874323`

To get a custom modified KML file (using form data fields) of the ride you may type:

`curl -X POST -F "color=red" -F "thickness=4" -F "id=874323" -F "start=2014-02-06 14:30" -F "end=2014-02-06 14:32" -F "accuracy=50" api.pedal.cs.pdx.edu/kml`

The route will:

* Have the route colored with a red line
* draw the line using a thickness of 4
* involve points from the 874323 route id
* use points after Feb 6, 2014 @ 2:30pm Pacific Time
* use points before Feb 6, 2014 @ 2:32pm Pacific Time
* only include points that were accurate up to 50 meters

Error Responses
---------------
Sending a request to the API requires a somewhat particular syntax. Error codes are available
to help you identify what went wrong in such cases. When an Error does occur, the requester will
receive both a `description` of the error as well as an error `code` that can help locate where
the issue arose.

| Code  | Description                                |
| :---: | :-----------                               |
| 100   | Non Existent URL                           |
| 200   | Ride ID does not exist on disk             |
| 300   | Request was not in JSON format             |
| 310   | 'version' field missing in POST data       |
| 311   | 'hash' field missing in POST data          |
| 312   | 'points' field missing in POST data        |
| 320   | Missing location information in point data |
| 400   | Missing form data                          |
| 410   | 'rideid' field missing in form data        |
| 411   | 'thinkness' field missing in form data     |
| 412   | 'accuracy' field missing in form data      |
| 413   | 'start' field missing in form data         |
| 414   | 'end' field missing in form data           |
| 415   | 'color' field missing in form data         |


Install
-------
To run this application locally, you may want to use a 
[virtual environment](VirtualEnvironment/run_locally.md) to handle dependencies.
