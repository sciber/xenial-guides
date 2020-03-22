Xenial guides generator, guides packager and guides store
=========================================================

This repository provides _dist_ directory where are stored guides archives which can be loaded into and displayed by 
[xenial](https://github.com/sciber/xenial) app. A dummy guide content (JSON files accompanied with corresponding media 
files) can be generated using GuideGenerator class from _guide_generator.py_ module. GuidePackager class from 
_guide_packager.py_ module packages a guide files into an archives which can be imported into 
[xenial](https://github.com/sciber/xenial) app.

Modules API and guide format is experimental and highly unstable!


Specification
-------------

Current archive file format version: 0.1 

Xenial guide archive files are zip archives created by compressing the guide description file (_guide.json_), sqlite3 
database file storing the guide content (_guide.db_), and directories with the guide icons (_/icons_) and multimedia 
files (_/media_).   

### The guide description file _guide.json_

The file contains:
- guide name which is also the name of the guide archive file (followed by _.zip_ extension), 
- version of the guide format following semantic versioning pattern,
- path to the guide icon file,
- guide title (a sentence),
- guide description (one paragraph of information pertinent to the guide),
- language in which the guide is written (language name and its abbreviation/code),
- place from which the guide navigates (a geographical starting point of a planned journey),
- place to which the guide navigates (a destination of the journey),
- guide content represented as a list of the guide's selected articles in predefined order.

### The guide content file _guide.db_

The file is sqlite3 database which stores data related to:
- the guides articles,
- bookmarks referencing articles,
- categories to which the articles belongs based on tags they share,
- tags assigned to the articles and/or categories.

#### Articles data tables

Articles data are split between __articles__ table storing an articles "header" information and __articles_blocks__ 
table which binds an article's header information with corresponding content blocks. __articles__ table stores 
an articles id, name, path to an icon file, title and synopsis. __articles_blocks__ table records pair articles' content
blocks (together with a block's types and order within the corresponding article) with headers of articles, to which 
they belong.  

Currently, there are five types of articles content blocks and blocks of each type are stored in separate tables:
- subtitle blocks are stored in __subtitle_blocks__ table (fields are subtitle block id and subtitle text),
- paragraph blocks are stored in __paragraph_blocks__ table (fields are paragraph block id and paragraph text),
- image blocks are stored in __image_blocks__ table (fields are image block id, path to the image source file and 
  the image capttion text),
- audio blocks are stored in __audio_blocks__ table (fields are audio block id, path to the audio source file, audio 
  length and the audio caption text),
- video blocks are stored in __video_blocks__ table (fields are video block id, path to the video source file, video
  length, video aspect ratio, path to video cover image source and the video caption text).

To unburden the guide browsing application ([xenial](https://github.com/sciber/xenial)), the database files contains __article_block_search__ table for fulltext 
search the guides articles content blocks using sqlite3 fts4 module. The table's fields are article id, block order, 
block type, block id and block text (content blocks of every type has only one text field, however this will probably 
change in future versions of the guide format).

#### Bookmarks data table

References to articles can be remembered in __bookmarks__ table, where the stored data are bookmark id, id of remembered
article and time when the bookmark was created.

#### Categories data tables

Categories data are stored in __categories__ table, which records store a category's id, name, path to an icon file and 
short description. A pivot table __tags_categories__ binds a category with its assigned tags.

#### Tags data table

Tags data are stored in __tags__ table, comprising tags id and name. An assignment of a tag to an article or category is 
managed through __tags_articles__ and __tags_categories__ pivot tables as described above.   

### The guide icons directory _icons_

The directory contains following three subdirectories: _articles_, _categories_, and _guide_. In these directories are 
stored icons of the guide's articles, categories, and an icon of the guide itself.  

### The guide media directory _media_

The directory contains three subdirectories - _image_, _audio_, and _video_. Source files of images presented in 
the guides articles are stored _image_ directory. Articles' audio files are stored in _audio_ directory. In _video_
directory there are stored articles' video files accompanied with corresponding cover image files.
