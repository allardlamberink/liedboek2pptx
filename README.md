# liedboek2pptx
A python script to automatically fill a PowerPoint template from a liedboek.nu zip-file

Python pptx generator for Hervgemb:

Minimum Python version: minimal 2.6 (because of pptx)
As of 20231104 tested and running on Python 3.10.6

Default image size from liedboek online: 1600x1200

The progresbar library is a forked version of https://github.com/Jaza/fotojazz

APP FLOW
1) /                - upload file
2) /sortliturgie    - order songs + edit church service data
3) /summary         - last check / overview
4) /                - generate pptx slides/ download pptx


enable debugging mode by setting environment variable:

  `export FLASK_ENV=development`


  `docker build -t liedboek2pptx .`

  ```docker run --env-file liedboek2pptx.env -d --name liedboek2pptx_01 -p 8000:80 liedboek2pptx```


Manually copy liedboek2pptx.env and app/projectie-415-muziek-couplet-cropped.png to the webserver before executing docker build on the webserver. These files are excluded from the git repo because they contain sensitive information or are protected by copyright laws.
