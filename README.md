Sirobutton
====

Sirobutton is a web application with which you can search and listen a Siro-chan's voice from all subtitles.

## Demo

see [sirobutton.herokuapp](https://sirobutton.herokuapp.com/) for more details.

## How to add subtitles to the db

1. Use [get-youtube-captions](https://github.com/KKawamura1/get-youtube-captions) to dump the pkl binary data (say a.pkl).
2. Run `python manage.py update_database < a.pkl`.
3. And that's all!

## Author

- Keigo Kawamura (Department of Electrical Engineering and Information Systems (EEIS), Graduate School of Engineering, The University of Tokyo)

 - kkawamura@logos.t.u-tokyo.ac.jp
