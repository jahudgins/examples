# Proposal #

I took a set of family photos and realized afterwards that the background has a lot of unwanted detail (fire extinguisher, signs on wall, etc.). I will make a program that automatically removes the unwanted detail from the background. Another option will be to replace the entire background with the desired color.
 
I will pay particular attention to ensuring that the boundary between the old foreground and the new background is seamless.

[Example source photo](https://plus.google.com/u/0/photos/110249926708885809048/albums/6134032771921818673/6134034092345489618?pid=6134034092345489618&oid=110249926708885809048)


# Initial Ideas #

* Edge detection to determine all objects in a scene.
* Attempt to identify materials:
    shade changes OK -- especially within a reasonable locality
* Median/mode (buckets) colors to determine background colors.
* Use gradient direction and background color along borders to remove background color and replace as alpha
* Object identification:
    - Use entire object not just border
    - Train neural net to understand a person
    - Look for eyes
    - Create an object "signature" use KNN or other clustering algorithm to match with training examples
    - Look for "bad objects" --> any simple geometry (cylindrical, rectangular, )
    - Find a head/body
* Outside-in left-top-right sides are all background select all objects crossing those boundaries
* Regardless of object identification, we must find the background color because of gaps between people
* Interactivity
    - Define smallest region that contains all people
    - find good values for constants
* All people are interconnected
* Need more global understanding
* Use pyramids to get anti-aliasing


# Investigations #

## Search for ##
* [Static Background Extraction](http://www.google.com/webhp?#q=static%20background%20extraction)
* [Static Background Detection](http://www.google.com/webhp?#q=Static%20Background%20Detection)
* [Background Filter](http://www.google.com/webhp?#q=Background%20Filter)
* [Automatic Background Removal](http://www.google.com/webhp?#q=Automatic%20Background%20Removal)

## Top Results ##
### [Wikipedia](http://en.wikipedia.org/wiki/Background_subtraction) ###
* Frame differencing (not applicable, requires motion)
* Mean filter (not applicable, requires motion)
* MOG Background Subtraction: seems much more promising based on color distribution
* Reference to [OpenCV BG/FG Subtraction](http://docs.opencv.org/trunk/doc/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html)
* Results of https://www.academia.edu/691079/Subspace_learning_for_background_modeling_A_survey seem to demonstrate that it is hard to get an algorithm to match the ground truth

"static" often used to describe a background that doesn't move instead of a static picture

# Material Signatures #
* parallel processing
* pattern recognition
* pattern gerneation
