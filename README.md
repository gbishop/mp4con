# Mp4 Converter

## Summary
A small web-app for converting mp4's provided by the Minimal Eyereader to
csv's. Currently a WIP; the app is up and running, but improvements are being
added. The current data flow is as follows: MP4 is uploaded to the server in a
temporary folder, from there the the first 50 frames, each 5 seconds (50
frames) apart are extracted using converter.split() and put in another
temporary folder. From there The user selects the initial frame, a more
specific initial frame if needed, an end frame, a more specific end frame if
needed, and the dimensions of the text and image on the first frame. All of
this is handled client-sided via javascript, it's then sent as a get request to
the server. The user is redirected to the initial upload page while the all the
arguments as well as the saved video are passed into converter.mp4con, where
the data is converted into a csv.

## Things To Do
 - Convert to ReactJS and rewrite Javascript in general (make it more modular, as
of now it's just a single script w/ no re-usability)
 - Profile and rewrite mp4con to increase speed.
 - Imporve UI, right now it's very minimalistic
## Things Done
 - Create a functional web app
 - Improve the split method, increase modularity and remove redundancy
 - Reduced memory usage 
