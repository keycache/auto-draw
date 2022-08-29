# Auto Colouring Image

This project is a proof of concept for auto generating a randomly generating a colourized image based given an empty one.


## TODO
 - [x] Preprocess image
	 - [x] Resize - ensure is not too big
	 - [x] convert to `grayscale`
	 - [x] make it a binary image - either `black` or `whtie`
 - [ ] Build a container(class) for representing Image
	 - [x] Identify Image Segments - contiguously connected points with the same color
	 - [x] Identify if the image segments are colour eligible
	 - [x] Helper methods
		 - [x] Save image representation as `pkl` file
		 - [x] Create a randomized coloured version(s) of the image
		 - [x] load the `pkl` file for processing in future
 - [ ] logging
 - [x] Save snapshots
 - [ ] Make Video
	 - [ ] leverage `pymovie`
	 - [ ] user audio
	 - [ ] transitions
 - [ ] Incremental sketcher
	 - [x] load the `pkl` file
	 - [x] Define snapshot thresholds
	 - [x] build sorting for `image segents` and the `point`s within
	 - [x] rendering scheme using snapshot thresholds and sorters

----------