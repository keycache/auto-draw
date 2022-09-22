# Auto Colouring Image

This project is a proof of concept for auto generating a randomly generating a colourized image, given an empty, un-coloured one.


## TODO
 - [x] Preprocess image
	 - [x] Resize - ensure is not too big
	 - [x] convert to `grayscale`
	 - [x] make it a binary image - either `black` or `whtie`
 - [x] Build a container(class) for representing Image
	 - [x] Identify Image Segments - contiguously connected points with the same color
	 - [x] Identify if the image segments are colour eligible
	 - [x] Helper methods
		 - [x] Save image representation as `pkl` file
		 - [x] Create a randomized coloured version(s) of the image
		 - [x] load the `pkl` file for processing in future
 - [ ] logging
 - [x] `click` integration for better cli experience
 - [x] Save snapshots
 - [x] Make Video
	 - [x] leverage `pymovie`
	 - [x] user audio
	 - [x] transitions
	 - [x] compose videos
	 - [ ] Make it work with relative paths.
 - [x] Incremental sketcher
	 - [x] load the `pkl` file.
	 - [x] Define snapshot thresholds.
	 - [x] build sorting for `image segments` and the `point`s within.
	 - [x] rendering scheme using snapshot thresholds and sorters.
- [x] Thumbnail Generator
	 - [x] Create vanilla thumbnail.
	 - [ ] Generate final thumbnail
	 	- [ ] Compose images
		- [ ] Text Placement
		- [ ] Image size control



----------

## How to run?

### Image/Binary Generation

`image_orchestrator.py` generates the `pkl` files. These file are `python object` representation of the given image.

`python image_orchestrator.py --image-path .data/images/{image_name}.jpeg --target-dir .data/images/{image_name}/bin`

### Image Sketcher
`sketcher.py` generates the individual frames given a `pkl` file. This `pkl` file is generated from the previous step.

`python sketcher.py --binary-file-path .data/images/{image_name}/bin/{image_pkl_file}.pkl --mode=offline`

### Movie Maker
`movie_maker.py` generates a final rendered video file. As of now, `movie_maker` needs these files
* `intro video`
* `outro video`
* `background music`
* `shadow image`


Also, the below directories
* `source` - the directory that holds the incremental images
* `target` - the output directory.

**NOTE** The `movie_maker.py` uses `moviepy`. We NEED to pass fully qualified paths to ensure this works a 100% of the time(for now).  There is an open task to get it working with relative paths.

`python movie_maker.py --intro-path data/assets/intro.mp4 --outro-path /data/assets/outro.mp4 --bg-audio-path /data/assets/music/the-sea-is-calling-99289.mp3 --shadow-path /data/assets/shadow.png --source /data/images/{image_name}/snapshots --target /data/images/{image_name}/video --target-name final.mp4`


### Thumbnail Maker
`thumbnail_maker.py` generates a thumbnail to be used for cover for video/preview.

`python thumbnail_maker.py --base-image .data/images/{image_path} --rendered-image .data/images/{image_name}/out/{image_path} --target-dir .data/images/{image_name}/video --preview 1`