'''
Xenial dummy guides generator
=======================

This module contains class for generating xenia dummy guides, which are consumed by the xenial app.

Modules API and guide format is experimental and highly unstable.
'''

import os
import random
import json
from faker import Faker
import shutil
from zipfile import ZipFile

fake = Faker()

DIST_PATH = 'dist'
TMP_PATH = 'tmp'

ARTICLES_PATH = 'articles'

MEDIA_PATH = 'media'
IMAGE_PATH = os.path.join(MEDIA_PATH, 'image')
AUDIO_PATH = os.path.join(MEDIA_PATH, 'audio')
VIDEO_PATH = os.path.join(MEDIA_PATH, 'video')

ICONS_PATH = 'icons'
GUIDE_ICON_PATH = os.path.join(ICONS_PATH, 'guide')
CATEGORIES_ICONS_PATH = os.path.join(ICONS_PATH, 'categories')
ARTICLES_ICONS_PATH = os.path.join(ICONS_PATH, 'articles')


MAX_GUIDE_TITLE_LENGTH = 8
MAX_GUIDE_DESCRIPTION_LENGTH = 4

MIN_NUM_TAGS = 10
MAX_NUM_TAGS = 20

MIN_NUM_CATEGORIES = 3
MAX_NUM_CATEGORIES = 10
MIN_NUM_CATEGORY_TAGS = 1
if MIN_NUM_CATEGORY_TAGS > MAX_NUM_TAGS:
    raise ValueError('MIN_NUM_CATEGORY_TAGS cannot be bigger than MAX_NUM_TAGS')
MAX_NUM_CATEGORY_TAGS = 3
MAX_CATEGORY_NAME_LENGTH = 6
MAX_CATEGORY_DESCRIPTION_LENGTH = 3

MIN_NUM_ARTICLES = 8
MAX_NUM_ARTICLES = 15
MIN_NUM_ARTICLE_TAGS = 0
if MIN_NUM_CATEGORY_TAGS > MAX_NUM_TAGS:
    raise ValueError('MIN_NUM_ARTICLE_TAGS cannot be bigger than MAX_NUM_TAGS')
MAX_NUM_ARTICLE_TAGS = 9
MAX_ARTICLE_NAME_LENGTH = 6
MAX_ARTICLE_TITLE_LENGTH = 9
MIN_ARTICLE_SYNOPSIS_LENGTH = 2
MAX_ARTICLE_SYNOPSIS_LENGTH = 5
MAX_NUM_ARTICLE_CONTENT_ITEMS = 20
MAX_ARTICLE_PARAGRAPH_LENGTH = 5
MAX_ARTICLE_MEDIA_CAPTION_LENGTH = 4

MIN_NUM_BOOKMARKS = 3
MAX_NUM_BOOKMARKS = MIN_NUM_ARTICLES

COUNTRIES = ['Germany', 'Greece', 'Hungary', 'Ireland', 'Serbia', 'Slovakia', 'Syria', 'Turkey']
LANGUAGES = [('Arabic', 'ar'),
             ('English', 'en'),
             ('German', 'de'),
             ('Greek', 'el'),
             ('Hungarian', 'hu'),
             ('Irish', 'ga'),
             ('Kurdish', 'ku'),
             ('Serbian', 'sr'),
             ('Slovak', 'sk'),
             ('Turkish', 'tr')]


class GuideGenerator:
    @staticmethod
    def _generate_dummy_guide_categories(tags):
        """Private method used for generating the dummy guide's categories"""

        categories = []
        num_categories = random.randint(MIN_NUM_CATEGORIES, MAX_NUM_CATEGORIES)
        description_length = random.randint(1, MAX_CATEGORY_DESCRIPTION_LENGTH)
        category_icon_files = random.sample(os.listdir(CATEGORIES_ICONS_PATH), num_categories)
        for category_idx in range(num_categories):
            category_icon = category_icon_files[category_idx]
            num_category_tags = random.randint(MIN_NUM_CATEGORY_TAGS, MAX_NUM_CATEGORY_TAGS)
            categories.append({
                'icon': os.path.join(ICONS_PATH, CATEGORIES_ICONS_PATH, category_icon),
                'name': fake.sentence(nb_words=random.randint(1, MAX_CATEGORY_NAME_LENGTH))[:-1],
                'description': fake.paragraph(description_length),
                'tags': random.sample(tags, num_category_tags)
            })
            shutil.copy(os.path.join(CATEGORIES_ICONS_PATH, category_icon),
                        os.path.join(TMP_PATH, CATEGORIES_ICONS_PATH))
        with open(os.path.join(TMP_PATH, 'categories.json'), 'w') as f:
            json.dump(categories, f, indent=4)

    @staticmethod
    def _markup_text(text, articles):
        """Private method (naively) inserting kivy markups to the provided text"""

        markup_types = ['bold', 'italic', 'ref']
        words = text.split()
        markup_ratio = 1 / 8
        for markup_idx in range(round(len(words) * markup_ratio)):
            markup_type = random.choice(markup_types)
            markup_start = random.randint(0, len(words) - 1)
            markup_end = random.randint(markup_start, len(words) - 1)
            if markup_type == 'bold':
                words[markup_start] = '[b]' + words[markup_start]
                words[markup_end] = words[markup_end] + '[/b]'
            elif markup_type == 'italic':
                words[markup_start] = '[i]' + words[markup_start]
                words[markup_end] = words[markup_end] + '[/i]'
            elif markup_type == 'ref':
                article_ref = random.choice(articles)['name']
                words[markup_start] = f'[color=#008888][u][ref={article_ref}]' + words[markup_start]
                words[markup_end] = words[markup_end] + '[/ref][/u][/color]'
        markupped_text = ' '.join(words)
        return markupped_text

    @classmethod
    def _generate_dummy_guide_article_content_item(cls, current_item_type, articles):
        """Private method for generating a dummy guide article content item"""

        item = {'type': current_item_type}
        if current_item_type == 'subtitle':
            text = fake.paragraph()
            item['text'] = text
        elif current_item_type == 'paragraph':
            text = fake.paragraph(random.randint(1, MAX_ARTICLE_PARAGRAPH_LENGTH))
            item['text'] = cls._markup_text(text, articles)
        elif current_item_type == 'image':
            image_filename = random.choice(os.listdir(IMAGE_PATH))
            item['source'] = os.path.join(IMAGE_PATH, image_filename)
            shutil.copy(os.path.join(item['source']), os.path.join(TMP_PATH, item['source']))
            caption = fake.paragraph(random.randint(1, MAX_ARTICLE_MEDIA_CAPTION_LENGTH))
            item['caption'] = cls._markup_text(caption, articles)
        elif current_item_type == 'audio':
            audio_filename = random.choice(os.listdir(AUDIO_PATH))
            item['source'] = os.path.join(AUDIO_PATH, audio_filename)
            shutil.copy(os.path.join(item['source']), os.path.join(TMP_PATH, item['source']))
            caption = fake.paragraph(random.randint(1, MAX_ARTICLE_MEDIA_CAPTION_LENGTH))
            item['caption'] = cls._markup_text(caption, articles)
        elif current_item_type == 'video':
            video_filename = random.choice(os.listdir(VIDEO_PATH))
            item['source'] = os.path.join(VIDEO_PATH, video_filename)
            shutil.copy(os.path.join(item['source']), os.path.join(TMP_PATH, item['source']))
            caption = fake.paragraph(random.randint(1, MAX_ARTICLE_MEDIA_CAPTION_LENGTH))
            item['caption'] = cls._markup_text(caption, articles)
        else:
            raise ValueError('Provided a content item of unknown type.')
        return item

    @classmethod
    def _generate_dummy_guide_article_content(cls, article_head, articles):
        """Private method for generating a dummy guide article content"""
        article = {
            'name': article_head['name'],
            'icon': article_head['icon'],
            'tags': article_head['tags'],
        }
        content_items = []
        content_items.extend([{'type': 'title',
                               'text': article_head['title']},
                              {'type': 'synopsis',
                               'text': article_head['synopsis']}])
        content_types = ['subtitle', 'paragraph', 'image', 'audio', 'video']
        num_content_items = random.randint(1, MAX_NUM_ARTICLE_CONTENT_ITEMS)
        last_item_type = None
        for item_idx in range(num_content_items):
            if last_item_type != 'paragraph':
                current_item_type = 'paragraph'
            else:
                current_item_type = random.choice(content_types)
                if current_item_type == 'subtitle' and item_idx == (num_content_items - 1):
                    current_item_type = 'paragraph'

            content_items.append(cls._generate_dummy_guide_article_content_item(current_item_type, articles))
            last_item_type = current_item_type
        article['content'] = content_items
        with open(os.path.join(TMP_PATH, ARTICLES_PATH, article['name'] + '.json'), 'w') as f:
            json.dump(article, f, indent=4)

    @staticmethod
    def _generate_dummy_guide_bookmarks(articles_heads):
        bookmarks = []
        num_bookmarks = random.randint(MIN_NUM_BOOKMARKS, len(articles_heads))
        bookmarked_article = random.sample(articles_heads, num_bookmarks)
        for article in bookmarked_article:
            bookmarks.append({
                'article_name': article['name'],
                'article_title': article['title'],
                'created_at': str(fake.date_between(start_date="-30y", end_date="today"))
            })
        with open(os.path.join(TMP_PATH, 'bookmarks.json'), 'w') as f:
            json.dump(bookmarks, f, indent=4)

    @classmethod
    def _generate_dummy_guide_articles(cls, tags):
        """Private method fro generating a dummy guide articles"""

        os.mkdir(os.path.join(TMP_PATH, ARTICLES_PATH))
        os.mkdir(os.path.join(TMP_PATH, MEDIA_PATH))
        os.mkdir(os.path.join(TMP_PATH, IMAGE_PATH))
        os.mkdir(os.path.join(TMP_PATH, AUDIO_PATH))
        os.mkdir(os.path.join(TMP_PATH, VIDEO_PATH))
        articles_heads = []
        num_articles = random.randint(MIN_NUM_ARTICLES, MAX_NUM_ARTICLES)
        article_icon_files = random.sample(os.listdir(ARTICLES_ICONS_PATH), num_articles)
        for article_idx in range(num_articles):
            num_article_tags = random.randint(MIN_NUM_ARTICLE_TAGS, MAX_NUM_ARTICLE_TAGS)
            synopsis_length = random.randint(MIN_ARTICLE_SYNOPSIS_LENGTH, MAX_ARTICLE_SYNOPSIS_LENGTH)
            article_icon = article_icon_files[article_idx]
            articles_heads.append({
                'icon': os.path.join(ARTICLES_ICONS_PATH, article_icon),
                'name': fake.sentence(nb_words=random.randint(1, MAX_ARTICLE_NAME_LENGTH))[:-1],
                'title': fake.sentence(nb_words=random.randint(1, MAX_ARTICLE_TITLE_LENGTH))[:-1],
                'synopsis': fake.paragraph(synopsis_length),
                'tags': random.sample(tags, num_article_tags),
            })
            shutil.copy(os.path.join(ARTICLES_ICONS_PATH, article_icon),
                        os.path.join(TMP_PATH, ARTICLES_ICONS_PATH))

        for article_head in articles_heads:
            cls._generate_dummy_guide_article_content(article_head, articles_heads)

        cls._generate_dummy_guide_bookmarks(articles_heads)

        with open(os.path.join(TMP_PATH, 'articles.json'), 'w') as f:
            json.dump(articles_heads, f, indent=4)

    @staticmethod
    def _generate_dummy_guide_content_list():
        with open(os.path.join(TMP_PATH, 'articles.json'), 'r') as f:
            articles = json.load(f)
        articles_names_titles = random.sample([(article['name'], article['title']) for article in articles],
                                              len(articles))
        return articles_names_titles

    @staticmethod
    def _reset_tmp_dir():
        """Private method for resetting tmp directory, in which the generated dummy guide components
        are temporarily stored before packing
        """
        if os.path.isdir(TMP_PATH):
            shutil.rmtree(TMP_PATH)
        os.mkdir(TMP_PATH)
        os.mkdir(os.path.join(TMP_PATH, ICONS_PATH))
        os.mkdir(os.path.join(TMP_PATH, GUIDE_ICON_PATH))
        os.mkdir(os.path.join(TMP_PATH, CATEGORIES_ICONS_PATH))
        os.mkdir(os.path.join(TMP_PATH, ARTICLES_ICONS_PATH))

    @staticmethod
    def _dist_pack_dummy_guide(guide_name):
        """Private methods which packs all dummy guide components into single archive file"""

        file_paths = []
        working_dir = os.getcwd()
        os.chdir(TMP_PATH)
        for root, directory, files in os.walk('.'):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)

        with ZipFile(f'{guide_name}.zip', 'w') as zip:
            for file in file_paths:
                zip.write(file)

        os.chdir(working_dir)
        os.rename(os.path.join(TMP_PATH, f'{guide_name}.zip'), os.path.join(DIST_PATH, f'{guide_name}.zip'))

    @classmethod
    def generate_dummy_guide(cls, guide_name):
        """Public method for generating dummy guide"""

        cls._reset_tmp_dir()

        guide_icon = random.choice(os.listdir(GUIDE_ICON_PATH))
        from_country, to_country = random.sample(COUNTRIES, 2)
        description_length = random.randint(1, MAX_GUIDE_DESCRIPTION_LENGTH)
        num_tags = random.randint(MIN_NUM_TAGS, MAX_NUM_TAGS)
        tags = fake.words(num_tags)

        cls._generate_dummy_guide_categories(tags)
        cls._generate_dummy_guide_articles(tags)

        guide = {
            'name': guide_name,  # is the guide file name without the zip extension
            'version': '0.1',
            'icon': os.path.join(GUIDE_ICON_PATH, guide_icon),
            'title': fake.sentence(nb_words=random.randint(1, MAX_GUIDE_TITLE_LENGTH))[:-1],
            'description': fake.paragraph(description_length),
            'lang': random.choice(LANGUAGES),
            'from_place': from_country,
            'to_place': to_country,
            # 'tags': tags  # commented out because it will be generated from articles and categories during import
            'content': cls._generate_dummy_guide_content_list()
        }
        os.remove(os.path.join(TMP_PATH, 'articles.json'))  # all articles in the intended order are already listed in the guide['content']

        shutil.copy(os.path.join(GUIDE_ICON_PATH, guide_icon),
                    os.path.join(TMP_PATH, GUIDE_ICON_PATH))

        with open(os.path.join(TMP_PATH, 'guide.json'), 'w') as f:
            json.dump(guide, f, indent=4)

        cls._dist_pack_dummy_guide(guide_name)
        shutil.rmtree(TMP_PATH)  # Clean temporary directory for the guide assembling when finished


if __name__ == '__main__':
    guide_name = input('Guide name: ').lower().replace(' ', '_')
    if not guide_name:
        guide_name = 'dummy'

    GuideGenerator.generate_dummy_guide(guide_name)
