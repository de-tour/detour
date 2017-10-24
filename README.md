![Take a detour!](public/images/detour-banner.png)

De-tour
=======

We as a team shared a common problem: playing Spotify® music. The music files are protected by a controversial technology called [Encrypted Media Extensions](https://www.defectivebydesign.org/drm-in-web-standards). This DRM technique limits a user's freedom. One will find it difficult to use DRM-protected contents in Firefox and its variants.

Therefore, we put together De-tour during DubHacks 2017. De-tour is a web crawler that finds non-DRM media by looking up meta search engines, Internet archives, and crowd funding platforms. It automates the complicated search process for DRM-free media.

## Install

To use De-tour, first you need to create a virtual environment using Python 3 and activate it.

```bash
# create a virtual environment
mkdir detour-venv
cd detour-venv
python3 -m venv .
# activate the virtual environment
source ./bin/activate
```

Make sure you are in the virtual environment. Now, clone the source code and then install the dependencies.

```python
git clone https://github.com/de-tour/detour.git
cd detour
pip install -r requirements.txt
```

Troubleshooting: if you ran into a compilation error saying `<Python.h>` was not found, then you may have to install the Python 3 header files. On Debian-based GNU/Linux system, run the following command.

```bash
sudo apt install python3-dev
```

On Windows, you may have to follow the URL mentioned in the error message to install the compilers provided by Microsoft.

## Run

Make sure you are in the virtual environment. Then run the following commands.

```bash
chmod +x start.py
./start.py
```

Now you should be able to see the landing page at http://127.0.0.1:27900/

## Status of this project

At DubHacks, we put together De-tour in literally 24 hours. De-tour is a working prototype but not yet a finished program. We will continue working on this free software. We as a team are going to make De-tour more accessible and more efficient.

## Contact

Project Owner: Flynn [`<put_my_github_id_here [at] uw.edu>`](https://github.com/flynn16?tab=stars)

[![DRM-FREE](https://static.fsf.org/dbd/label/DRM-free label dropshadow 125.en.png)](https://www.defectivebydesign.org/drm-free)
