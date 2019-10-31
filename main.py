'''
Xenial guides generator
=======================

This module contains class for generating xenia guides, which are consumed by the xenial app.

Modules API and guide format is experimental and highly unstable.
'''

import os
import random
import json
from faker import Faker
import shutil
import tarfile

fake = Faker()

DIST_PATH = 'dist'
TMP_PATH = 'tmp'
TMP_ICONS_PATH = os.path.join(TMP_PATH, 'icons')
TMP_GUIDES_ICONS_PATH = os.path.join(TMP_ICONS_PATH, 'guides')
TMP_CATEGORIES_ICONS_PATH = os.path.join(TMP_ICONS_PATH, 'categories')
TMP_ARTICLES_ICONS_PATH = os.path.join(TMP_ICONS_PATH, 'articles')
TMP_CONTENT_PATH = os.path.join(TMP_PATH, 'content')
TMP_MEDIA_PATH = os.path.join(TMP_CONTENT_PATH, 'media')
TMP_IMAGE_PATH = os. path.join(TMP_MEDIA_PATH, 'image')
TMP_AUDIO_PATH = os. path.join(TMP_MEDIA_PATH, 'audio')
TMP_VIDEO_PATH = os. path.join(TMP_MEDIA_PATH, 'video')

ICONS_PATH = 'icons'
ARTICLES_ICONS_PATH = os.path.join(ICONS_PATH, 'articles')
CATEGORIES_ICONS_PATH = os.path.join(ICONS_PATH, 'categories')
GUIDES_ICONS_PATH = os.path.join(ICONS_PATH, 'guides')

ARTICLE_MEDIA_PATH = 'media'
ARTICLE_IMAGE_PATH = os.path.join(ARTICLE_MEDIA_PATH, 'image')
ARTICLE_AUDIO_PATH = os.path.join(ARTICLE_MEDIA_PATH, 'audio')
ARTICLE_VIDEO_PATH = os.path.join(ARTICLE_MEDIA_PATH, 'video')

MAX_GUIDE_TITLE_LENGTH = 10
MAX_GUIDE_DESCRIPTION_LENGTH = 4

MIN_NUM_TAGS = 10
MAX_NUM_TAGS = 20

MIN_NUM_CATEGORIES = 3
MAX_NUM_CATEGORIES = 10
MIN_NUM_CATEGORY_TAGS = 1
if MIN_NUM_CATEGORY_TAGS > MAX_NUM_TAGS:
    raise ValueError('MIN_NUM_CATEGORY_TAGS cannot be bigger than MAX_NUM_TAGS')
MAX_NUM_CATEGORY_TAGS = 5
MAX_CATEGORY_NAME_LENGTH = 6
MAX_CATEGORY_DESCRIPTION_LENGTH = 3

MIN_NUM_ARTICLES = 8
MAX_NUM_ARTICLES = 15
MIN_NUM_ARTICLE_TAGS = 0
if MIN_NUM_CATEGORY_TAGS > MAX_NUM_TAGS:
    raise ValueError('MIN_NUM_ARTICLE_TAGS cannot be bigger than MAX_NUM_TAGS')
MAX_NUM_ARTICLE_TAGS = 8
MAX_ARTICLE_TITLE_LENGTH = 9
MIN_ARTICLE_SYNOPSIS_LENGTH = 2
MAX_ARTICLE_SYNOPSIS_LENGTH = 5
MAX_NUM_ARTICLE_CONTENT_ITEMS = 20
MAX_ARTICLE_PARAGRAPH_LENGTH = 5
MAX_ARTICLE_MEDIA_CAPTION_LENGTH = 4

COUNTRIES = ['Germany', 'Greece', 'Hungary', 'Ireland', 'Serbia', 'Slovakia', 'Syria', 'Turkey']
LANGUAGES = ['Arabic', 'English', 'German', 'Greek', 'Hungarian', 'Irish', 'Kurdish', 'Serbian', 'Slovak', 'Turkish']


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
                'id': category_idx,
                'icon': category_icon,
                'name': fake.sentence(nb_words=random.randint(1, MAX_CATEGORY_NAME_LENGTH))[:-1],
                'description': fake.paragraph(description_length),
                'tags': random.sample(tags, num_category_tags)
            })
            shutil.copy(os.path.join(CATEGORIES_ICONS_PATH, category_icon), TMP_CATEGORIES_ICONS_PATH)
        with open(os.path.join(TMP_PATH, 'categories.json'), 'w') as f:
            json.dump(categories, f)

    @staticmethod
    def _markup_text(text, num_articles):
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
                article_ref = str(random.randint(0, num_articles - 1))
                words[markup_start] = f'[color=#008888][u][ref={article_ref}]' + words[markup_start]
                words[markup_end] = words[markup_end] + '[/ref][/u][/color]'
        markupped_text = ' '.join(words)
        return markupped_text

    @classmethod
    def _generate_dummy_guide_article_content_item(cls, current_item_type, num_articles):
        """Private method fro generating a dummy guide article content item"""

        item = {'type': current_item_type}
        if current_item_type == 'subtitle':
            text = fake.paragraph()
            item['text'] = cls._markup_text(text, num_articles)
        elif current_item_type == 'paragraph':
            text = fake.paragraph(random.randint(1, MAX_ARTICLE_PARAGRAPH_LENGTH))
            item['text'] = cls._markup_text(text, num_articles)
        elif current_item_type == 'image':
            item['source'] = random.choice(os.listdir(ARTICLE_IMAGE_PATH))
            shutil.copy(os.path.join(ARTICLE_IMAGE_PATH, item['source']), os.path.join(TMP_IMAGE_PATH, item['source']))
            caption = fake.paragraph(random.randint(1, MAX_ARTICLE_MEDIA_CAPTION_LENGTH))
            item['caption'] = cls._markup_text(caption, num_articles)
        elif current_item_type == 'audio':
            item['source'] = random.choice(os.listdir(ARTICLE_AUDIO_PATH))
            shutil.copy(os.path.join(ARTICLE_AUDIO_PATH, item['source']), os.path.join(TMP_AUDIO_PATH, item['source']))
            caption = fake.paragraph(random.randint(1, MAX_ARTICLE_MEDIA_CAPTION_LENGTH))
            item['caption'] = cls._markup_text(caption, num_articles)
        elif current_item_type == 'video':
            item['source'] = random.choice(os.listdir(ARTICLE_VIDEO_PATH))
            shutil.copy(os.path.join(ARTICLE_VIDEO_PATH, item['source']), os.path.join(TMP_VIDEO_PATH, item['source']))
            item['screenshot'] = item['source'][:-3] + 'jpg'
            shutil.copy(os.path.join(ARTICLE_VIDEO_PATH, item['screenshot']), os.path.join(TMP_VIDEO_PATH, item['screenshot']))
            caption = fake.paragraph(random.randint(1, MAX_ARTICLE_MEDIA_CAPTION_LENGTH))
            item['caption'] = cls._markup_text(caption, num_articles)
        else:
            raise ValueError('Provided unknown type of a content item')
        return item

    @classmethod
    def _generate_dummy_guide_article_content(cls ,parent_article_id, num_articles):
        """Private method for generating a dummy guide article content"""

        content = []
        content_types = ['subtitle', 'paragraph', 'image', 'audio', 'video']
        num_content_items = random.randint(1, MAX_NUM_ARTICLE_CONTENT_ITEMS)
        last_item_type = None
        for item_idx in range(num_content_items):
            if last_item_type != 'paragraph':
                current_item_type = 'paragraph'
            else:
                current_item_type = random.choice(content_types)
            content.append(cls._generate_dummy_guide_article_content_item(current_item_type, num_articles))
            last_item_type = current_item_type
        with open(os.path.join(TMP_CONTENT_PATH, f'{parent_article_id}.json'), 'w') as f:
            json.dump(content, f)

    @classmethod
    def _generate_dummy_guide_articles(cls, tags):
        """Private method fro generating a dummy guide articles"""

        os.mkdir(TMP_CONTENT_PATH)
        os.mkdir(TMP_MEDIA_PATH)
        os.mkdir(TMP_IMAGE_PATH)
        os.mkdir(TMP_AUDIO_PATH)
        os.mkdir(TMP_VIDEO_PATH)
        articles = []
        num_articles = random.randint(MIN_NUM_ARTICLES, MAX_NUM_ARTICLES)
        article_icon_files = random.sample(os.listdir(ARTICLES_ICONS_PATH), num_articles)
        for article_idx in range(num_articles):
            num_article_tags = random.randint(MIN_NUM_ARTICLE_TAGS, MAX_NUM_ARTICLE_TAGS)
            synopsis_length = random.randint(MIN_ARTICLE_SYNOPSIS_LENGTH, MAX_ARTICLE_SYNOPSIS_LENGTH)
            article_icon = article_icon_files[article_idx]
            articles.append({
                'id': article_idx,
                'icon': article_icon,
                'title': fake.sentence(nb_words=random.randint(1, MAX_ARTICLE_TITLE_LENGTH))[:-1],
                'synopsis': fake.paragraph(synopsis_length),
                'tags': random.sample(tags, num_article_tags),
            })
            shutil.copy(os.path.join(ARTICLES_ICONS_PATH, article_icon), TMP_ARTICLES_ICONS_PATH)
            cls._generate_dummy_guide_article_content(article_idx, num_articles)

        with open(os.path.join(TMP_PATH, 'articles.json'), 'w') as f:
            json.dump(articles, f)

    @staticmethod
    def _reset_tmp_dir():
        """Private method for resetting tmp directory, in which the generated dummy guide components
        are temporarily stored before packing
        """
        if os.path.isdir(TMP_PATH):
            shutil.rmtree(TMP_PATH)
        os.mkdir(TMP_PATH)
        os.mkdir(TMP_ICONS_PATH)
        os.mkdir(TMP_GUIDES_ICONS_PATH)
        os.mkdir(TMP_CATEGORIES_ICONS_PATH)
        os.mkdir(TMP_ARTICLES_ICONS_PATH)

    @staticmethod
    def _dist_pack_dummy_guide(guide_name):
        """Private methods which packs all dummy guide components into single archive file"""

        tmp_filenames = os.listdir(TMP_PATH)
        with tarfile.open(os.path.join(DIST_PATH, f'{guide_name}.tgz'), 'w:gz') as tar:
            os.chdir(TMP_PATH)
            for filename in tmp_filenames:
                tar.add(os.path.join(filename))
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

    @classmethod
    def generate_dummy_guide(cls, guide_name):
        """Public method for generating dummy guide"""

        guide_icon = random.choice(os.listdir(GUIDES_ICONS_PATH))
        from_country, to_country = random.sample(COUNTRIES, 2)
        description_length = random.randint(1, MAX_GUIDE_DESCRIPTION_LENGTH)
        num_tags = random.randint(MIN_NUM_TAGS, MAX_NUM_TAGS)
        tags = fake.words(num_tags)
        guide = {
            'name': guide_name,
            'icon': guide_icon,
            'title': fake.sentence(nb_words=random.randint(1, MAX_GUIDE_TITLE_LENGTH))[:-1],
            'description': fake.paragraph(description_length),
            'lang': random.choice(LANGUAGES),
            'from_place': from_country,
            'to_place': to_country,
            'tags': tags
        }
        cls._reset_tmp_dir()
        shutil.copy(os.path.join(GUIDES_ICONS_PATH, guide_icon), TMP_GUIDES_ICONS_PATH)
        with open(os.path.join(TMP_PATH, 'guides.json'), 'w') as f:
            json.dump(guide, f)

        cls._generate_dummy_guide_categories(tags)
        cls._generate_dummy_guide_articles(tags)

        cls._dist_pack_dummy_guide(guide_name)
        shutil.rmtree(TMP_PATH)  # Clean temporary directory for the guide assembling when finished


if __name__ == '__main__':
    guide_name = input('Guide name: ')
    if not guide_name:
        guide_name = 'dummy'

    GuideGenerator.generate_dummy_guide(guide_name)
