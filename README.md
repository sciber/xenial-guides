Xenial guides store and generator
=================================

This module contains class for generating xenia guides, which are consumed 
by the [xenial](https://github.com/sciber/xenial) app.

Modules API and guide format is experimental and highly unstable.


Specification
-------------

Xenial guide archive files are zip compressed files created by compressing guide content files and corresponding
multimedia content using Python standard module zipfile. The guide content files are currently in the json format, 
however, they are planed to be transformed to application specific (simpliefied) markdown format. This expected 
format transition is accounted also in the following guide content json files.  
A guide content files are currently as follows:

### Guide guide.json file

A guide is defined by guide.json file located in the root of guide archive. 
The file contains:
- name of the guide (is the name of the guide archive file and also the name of folder where is located guide content
files after installation) 
- version (version of guide format; string)
- icon (relative path from guide root to the icon file; string)
- title (one sentence; string)
- description (one paragraph; string)
- language (in which the guide is written; tuple of language name and ist code)
- from place (geographical starting point of planned travel)
- to_place (destination)
- content (list of guide article titles/names in an arbitrary order; 
article names are with their relative path from the guide root)

### Categories categories.json file

Guide categories are listed in categories.json file located in the root of guide archive. 
Every category is described by:
- name (noun/noun and adjectives)
- icon (relative path from guide root the the icon file; string)
- description (one paragraph; string)
- tags (list of tags assigned to the category; maximum 3 words)

### Article article_filename.json file

A guide article is described by a json file composed of:
- name (is also name of the article file; without the path)
- icon (relative path from guide root the the icon file; string)
- tags (list of tags assigned to the article; maximum 3 words)
- article content (list of article content items)

#### Article content items

Some parts of items presented in articles are susceptible to be seasoned with kivy markup formatting.

Content of every article starts with 2 required items:
- title (one sentence; string)
- synopsis (one paragraph summary of the article content)

Rest of the article content is composed of variable list of:
- subtitles (string)
- paragraphs (string with markup)
- images (relative path to the resource) and corresponding caption (string with markup)
- reference to audio file (relative path to the resource) and corresponding caption (string with markup)
- reference to video file (relative path to the resource) and corresponding caption (string with markup)

Other article content types are expected to emerge from further application use and development. 