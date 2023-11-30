# UOCIS322 - Project 6
Author: Luke Marshall
Contact: LukeMArshall2222@gmail.com  

The purpose of this project is to implement an algorithm that acts as a brevet control time calculator, implement a mongodb database to be able to store, and later display, one set of page inputs at a time in the webpage, and implement a RESTful API so that CRUD methods may be implemented on the brevets collection using MongoEngine. A web page is implemented with HTML, AJAX, and a Flask server to create an interface with the calculator.

# Brevets Time Calculator

The algorithm calculates the open and close time for each control distance entered into the web page. The times are based on this distance, the overall distance of the entire brevet, and the start time of the brevet. Brevets can be 200, 400, 600, or 1000 kilometers in length and within each interval therin lies a maximum and minimum average speed that must be achieved by the rider for continuous riding and not being cut out of the brevet. The control time is calculated by using these interval average times and the intervals themselves, adding the amount of time that can or must be taken to complete each interval or portion of an interval to make a total time, and adding it to the start time of the brevet. The start control opens at start time and ends one hour thereafter. The end control timing is based on the length of the brevet, with the start time being based on the total distance whether it is exactly at that distance or slightly farther; and the close-time is based on specified timing for the end of the race, given by the organization.

# MongoDB web page implementation

MongoDB is implemented through the use of MongoENgine and its communication with the page is fascilitated by the use of the flask server and docker-compose. If appropriate inputs are made in the page and the 'Submit' button is pressed, the inputs will be saved in the database. If there is a saved inputs in the database, pressing the 'Display' button will display the latest inputs to have been submitted.

# RESTful API

* Implemented a RESTful API in `api/`:
	* Data schema using MongoEngine for Checkpoints and Brevets:
		* `Checkpoint`:
			* `distance`: float, required, (checkpoint distance in kilometers), 
			* `location`: string, optional, (checkpoint location name), 
			* `open_time`: datetime, required, (checkpoint opening time), 
			* `close_time`: datetime, required, (checkpoint closing time).
		* `Brevet`:
			* `length`: float, required, (brevet distance in kilometers),
			* `start_time`: datetime, required, (brevet start time),
			* `checkpoints`: list of `Checkpoint`s, required, (checkpoints).
	* RESTful API with the resource `/brevets/`:
		* GET `http://API:PORT/api/brevets` displays all brevets stored in the database.
		* GET `http://API:PORT/api/brevet/ID` displays brevet with id `ID`.
		* POST `http://API:PORT/api/brevets` inserts brevet object in request into the database.
		* DELETE `http://API:PORT/api/brevet/ID` deletes brevet with id `ID`.
		* PUT `http://API:PORT/api/brevet/ID` updates brevet with id `ID` with object in request.