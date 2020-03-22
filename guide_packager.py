"""
Xenial guides packager
======================

This module contains class for packaging xenial guides content.

Modules API and guide format is experimental and highly unstable.
"""

import ffmpeg
import json
import os
import shutil
import sqlite3
import re
from zipfile import ZipFile

DIST_PATH = os.path.join('dist', 'dummy')


class GuidePackager:
    @classmethod
    def pack(cls, guide_name, guide_path):
        """ Public method which stores guide content into sqlite database and packs it together with multimedia assets
            into a single zip archive file """

        cls._store_guide_content_in_db(guide_name, guide_path)
        cls._pack_guide_content_to_archive(guide_name, guide_path)

    @classmethod
    def _store_guide_content_in_db(cls, guide_name, guide_path):
        """ Private method which stores guide content into sqlite database """

        conn = sqlite3.connect(os.path.join(guide_path, 'guide.db'))

        cls._store_guide_categories_in_db(conn, guide_name, guide_path)
        cls._store_guide_articles_in_db(conn, guide_name, guide_path)
        cls._store_guide_bookmarks_in_db(conn, guide_path)

        conn.commit()
        conn.close()

    @staticmethod
    def _pack_guide_content_to_archive(guide_name, guide_path):
        """ Private method which packs guide stored in database together with its multimedia assets
            into a single zip archive file """

        file_paths = []
        project_root = os.getcwd()
        os.chdir(guide_path)
        for root, directory, files in os.walk('.'):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
        with ZipFile(f'{guide_name}.zip', 'w') as zipf:
            for file in file_paths:
                zipf.write(file)
        os.chdir(project_root)
        os.rename(os.path.join(guide_path, f'{guide_name}.zip'), os.path.join(DIST_PATH, f'{guide_name}.zip'))
        shutil.rmtree(guide_path)  # Delete temporary guide directory when finished

    @classmethod
    def _store_guide_categories_in_db(cls, conn, guide_name, guide_path):
        with open(os.path.join(guide_path, 'categories.json'), 'r') as f:
            categories = json.load(f)
        cls._create_categories_table(conn)
        cls._create_tags_table(conn)
        cls._create_tags_categories_table(conn)
        for category in categories:
            category_id = cls._insert_into_categories(
                conn, (category['name'],
                       os.path.join('guides', guide_name, category['icon']),
                       category['description']))
            for tag_name in set(category['tags']):
                tag_row = cls._fetchone_from_tags_where_name(conn, tag_name)
                if tag_row is not None:
                    tag_id = tag_row[0]
                else:
                    tag_id = cls._insert_into_tags(conn, tag_name)
                cls._insert_into_tags_categories(conn, (tag_id, category_id))
        os.remove(os.path.join(guide_path, 'categories.json'))

    @classmethod
    def _store_guide_articles_in_db(cls, conn, guide_name, guide_path):
        cls._create_articles_table(conn)
        cls._create_tags_articles_table(conn)
        cls._fill_articles_tags_articles_tables(conn, guide_name, guide_path)
        shutil.rmtree(os.path.join(guide_path, 'articles'))

        cls._create_articles_blocks_table(conn)
        cls._create_subtitle_blocks_table(conn)
        cls._create_paragraph_blocks_table(conn)
        cls._create_image_blocks_table(conn)
        cls._create_audio_blocks_table(conn)
        cls._create_video_blocks_table(conn)

        cls._fill_articles_content_block_tables(conn, guide_name, guide_path)
        cls._create_and_fill_article_block_search_table(conn)

    @classmethod
    def _store_guide_bookmarks_in_db(cls, conn, guide_path):
        with open(os.path.join(guide_path, 'bookmarks.json'), 'r') as f:
            bookmarks = json.load(f)
        cls._create_bookmarks_table(conn)
        for bookmark in bookmarks:
            article_id = cls._fetchone_from_articles_where_name(conn, bookmark['article_name'])[0]
            cls._insert_into_bookmarks(conn, (article_id, bookmark['created_at']))
        os.remove(os.path.join(guide_path, 'bookmarks.json'))

    @staticmethod
    def _create_categories_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE categories (
                            id integer PRIMARY KEY,
                            name text UNIQUE NOT NULL,
                            icon text,
                            description text
                        ); """)

    @staticmethod
    def _create_tags_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE tags (
                            id integer PRIMARY KEY,
                            name text UNIQUE NOT NULL
                        ); """)

    @staticmethod
    def _create_tags_categories_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE tags_categories (
                            tag_id integer NOT NULL,
                            category_id integer NOT NULL,
                            UNIQUE(tag_id, category_id)
                        ); """)

    @staticmethod
    def _insert_into_categories(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO categories (name, icon, description)
                        VALUES (?, ?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _fetchone_from_tags_where_name(conn, tag_name):
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM tags WHERE name=?; """, (tag_name,))
        return cur.fetchone()

    @staticmethod
    def _insert_into_tags(conn, tag_name):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO tags (name) VALUES (?); """, (tag_name,))
        return cur.lastrowid

    @staticmethod
    def _insert_into_tags_categories(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO tags_categories (tag_id, category_id)
                        VALUES (?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _create_articles_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE articles (
                            id integer PRIMARY KEY,
                            name text UNIQUE NOT NULL,
                            icon text,
                            title text,
                            synopsis text,
                            content text
                        ); """)

    @staticmethod
    def _create_tags_articles_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE tags_articles (
                            tag_id integer NOT NULL,
                            article_id integer NOT NULL,
                            UNIQUE(tag_id, article_id)
                        ); """)

    @classmethod
    def _fill_articles_tags_articles_tables(cls, conn, guide_name, guide_path):
        articles_jsons = [filename for filename in os.listdir(os.path.join(guide_path, 'articles'))]
        for article_json in articles_jsons:
            with open(os.path.join(guide_path, 'articles', article_json), 'r') as f:
                article = json.load(f)

            article_id = cls._insert_into_articles(
                conn, (article['name'],
                       os.path.join('guides', guide_name, article['icon']),
                       article['title'],
                       article['synopsis'],
                       json.dumps(article['content'])))

            for tag_name in set(article['tags']):
                tag_row = cls._fetchone_from_tags_where_name(conn, tag_name)
                if tag_row is not None:
                    tag_id = tag_row[0]
                else:
                    tag_id = cls._insert_into_tags(conn, tag_name)
                cls._insert_into_tags_articles(conn, (tag_id, article_id))

    @staticmethod
    def _create_articles_blocks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE articles_blocks (
                            article_id integer NOT NULL,
                            block_id integer NOT NULL,
                            block_order integer NOT NULL,
                            block_type text NOT NULL,
                            UNIQUE(article_id, block_id, block_order, block_type)
                        ); """)

    @staticmethod
    def _create_subtitle_blocks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE subtitle_blocks (
                            id integer PRIMARY KEY,
                            subtitle_text text NOT NULL
                        ); """)

    @staticmethod
    def _create_paragraph_blocks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE paragraph_blocks (
                            id integer PRIMARY KEY,
                            paragraph_text text NOT NULL
                         ); """)

    @staticmethod
    def _create_image_blocks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE image_blocks (
                            id integer PRIMARY KEY,
                            image_source text NOT NULL,
                            caption_text text
                        ); """)

    @staticmethod
    def _create_audio_blocks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE audio_blocks (
                            id integer PRIMARY KEY,
                            block_type text NOT NULL DEFAULT 'audio',
                            audio_source text NOT NULL,
                            audio_length real,
                            caption_text text
                        ); """)

    @staticmethod
    def _create_video_blocks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE video_blocks (
                            id integer PRIMARY KEY,
                            video_source text NOT NULL,
                            video_length real,
                            video_aspect_ratio text,
                            video_cover_source text,
                            caption_text text
                        ); """)

    @classmethod
    def _fill_articles_content_block_tables(cls, conn, guide_name, guide_path):
        articles_rows = cls._fetchall_id_name_content_from_articles(conn)
        articles_dicts = {row[1]: [row[0], row[2]] for row in articles_rows}
        for article_name in articles_dicts:
            article_id = articles_dicts[article_name][0]
            article_content = json.loads(articles_dicts[article_name][1])
            block_order = 0
            for block in article_content:
                if block['type'] == 'subtitle':
                    updated_refs_paragraph = cls._update_text_refs(block['text'], articles_dicts)
                    block_id = cls._insert_into_subtitle_blocks(conn, updated_refs_paragraph)
                elif block['type'] == 'paragraph':
                    updated_refs_paragraph = cls._update_text_refs(block['text'], articles_dicts)
                    block_id = cls._insert_into_paragraph_blocks(conn, updated_refs_paragraph)
                elif block['type'] == 'image':
                    guide_block_source = os.path.join('guides', guide_name, block['source'])
                    updated_refs_image_caption_text = cls._update_text_refs(block['caption'], articles_dicts)
                    block_id = cls._insert_into_image_blocks(conn,
                                                             (guide_block_source, updated_refs_image_caption_text))
                elif block['type'] == 'audio':
                    guide_block_source = os.path.join('guides', guide_name, block['source'])
                    probe = ffmpeg.probe(os.path.join(guide_path, block['source']))
                    audio_length = probe['format']['duration']
                    updated_refs_audio_caption_text = cls._update_text_refs(block['caption'], articles_dicts)
                    block_id = cls._insert_into_audio_blocks(conn,
                                                             (guide_block_source,
                                                              audio_length,
                                                              updated_refs_audio_caption_text))
                elif block['type'] == 'video':
                    guide_block_source = os.path.join('guides', guide_name, block['source'])
                    in_videofile_path = os.path.join(guide_path, block['source'])
                    probe = ffmpeg.probe(in_videofile_path)
                    video_length = probe['format']['duration']
                    video_aspect_ratio = next(stream['display_aspect_ratio'] for stream in probe['streams']
                                              if stream['codec_type'] == 'video')
                    cover_filename = os.path.splitext(block['source'])[0] + '.png'
                    out_imagefile_path = os.path.join(guide_path, cover_filename)
                    if not os.path.exists(out_imagefile_path):
                        try:
                            ffmpeg.input(in_videofile_path).output(out_imagefile_path, vframes=1).run()
                        except ffmpeg.Error as e:
                            print(e.stdout.decode('utf8'))
                            print(e.stderr.decode('utf8'))
                            exit(1)
                    video_cover_source = os.path.join('guides', guide_name, cover_filename)
                    updated_refs_video_caption_text = cls._update_text_refs(block['caption'], articles_dicts)
                    block_id = cls._insert_into_video_blocks(conn,
                                                             (guide_block_source,
                                                              video_length,
                                                              video_aspect_ratio,
                                                              video_cover_source,
                                                              updated_refs_video_caption_text))
                else:
                    continue
                cls._insert_into_articles_blocks(conn, (article_id, block_id, block_order, block['type']))
                block_order += 1

        cls._alter_table_articles_drop_column_content(conn)

    @staticmethod
    def _create_and_fill_article_block_search_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE VIRTUAL TABLE article_block_search 
                        USING fts4(article_id, block_order, block_type, block_id, block_text); """)

        cur.execute(""" INSERT INTO article_block_search
                        SELECT id AS article_id, -2 AS block_order, 'title' AS block_type, NULL AS block_id, title AS block_text 
                        FROM articles
                        UNION
                        SELECT id AS article_id, -1 AS block_order, 'synopsis' AS block_type, NULL AS block_id, synopsis AS block_text 
                        FROM articles
                        UNION
                        SELECT ab.article_id, ab.block_order, ab.block_type, ab.block_id, sub.subtitle_text AS block_text 
                        FROM articles_blocks AS ab
                        JOIN subtitle_blocks AS sub
                        ON sub.id=ab.block_id AND ab.block_type='subtitle'
                        UNION
                        SELECT ab.article_id, ab.block_order, ab.block_type, ab.block_id, pab.paragraph_text AS block_text 
                        FROM articles_blocks AS ab
                        JOIN paragraph_blocks AS pab
                        ON pab.id=ab.block_id AND ab.block_type='paragraph'
                        UNION
                        SELECT ab.article_id, ab.block_order, ab.block_type, ab.block_id, imb.caption_text AS block_text 
                        FROM articles_blocks AS ab
                        JOIN image_blocks AS imb
                        ON imb.id=ab.block_id AND ab.block_type='image'
                        UNION
                        SELECT ab.article_id, ab.block_order, ab.block_type, ab.block_id, aub.caption_text AS block_text 
                        FROM articles_blocks AS ab
                        JOIN audio_blocks AS aub
                        ON aub.id=ab.block_id AND ab.block_type='audio'
                        UNION
                        SELECT ab.article_id, ab.block_order, ab.block_type, ab.block_id, vib.caption_text as block_text 
                        FROM articles_blocks as ab
                        JOIN video_blocks AS vib
                        ON vib.id=ab.block_id AND ab.block_type='video'
                        ORDER BY article_id, block_order; """)
        conn.commit()

    @staticmethod
    def _insert_into_articles(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO articles (name, icon, title, synopsis, content)
                        VALUES (?, ?, ?, ?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _insert_into_tags_articles(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO tags_articles (tag_id, article_id)
                        VALUES (?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _fetchall_id_name_content_from_articles(conn):
        cur = conn.cursor()
        cur.execute(""" SELECT id, name, content FROM articles; """)
        return cur.fetchall()

    @staticmethod
    def _insert_into_subtitle_blocks(conn, text):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO subtitle_blocks (subtitle_text)
                        VALUES (?); """, (text,))
        return cur.lastrowid

    @staticmethod
    def _update_text_refs(text, articles_dicts):
        def replace_name_ref(matchobj):
            article_name = matchobj.group(1).strip()
            if article_name not in articles_dicts:
                replacement = '[ref=]'
            else:
                article_id = articles_dicts[article_name][0]
                replacement = '[ref={ref}]'.format(ref=article_id)
            return replacement

        result = re.sub(r'\[ref=(.*?)\]', replace_name_ref, text)
        return result

    @staticmethod
    def _insert_into_paragraph_blocks(conn, text):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO paragraph_blocks (paragraph_text)
                        VALUES (?); """, (text,))
        return cur.lastrowid

    @staticmethod
    def _insert_into_image_blocks(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO image_blocks (image_source, caption_text)
                        VALUES (?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _insert_into_audio_blocks(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO audio_blocks (audio_source, audio_length, caption_text)
                        VALUES (?, ?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _insert_into_video_blocks(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO video_blocks (video_source, video_length, video_aspect_ratio, video_cover_source, caption_text)
                        VALUES (?, ?, ?, ?, ?); """, values)
        return cur.lastrowid

    @staticmethod
    def _insert_into_articles_blocks(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO articles_blocks (article_id, block_id, block_order, block_type)
                        VALUES (?, ?, ?, ?); """, values)

    @staticmethod
    def _alter_table_articles_drop_column_content(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE articles_new (
                            id integer PRIMARY KEY,
                            name text UNIQUE NOT NULL,
                            icon text,
                            title text,
                            synopsis text
                        ); """)
        cur.execute(""" INSERT INTO articles_new (id, name, icon, title, synopsis)
                        SELECT id, name, icon, title, synopsis FROM articles; """)
        cur.execute(""" DROP TABLE articles; """)
        cur.execute(""" ALTER TABLE articles_new RENAME TO articles; """)
        conn.commit()

    @staticmethod
    def _create_bookmarks_table(conn):
        cur = conn.cursor()
        cur.execute(""" CREATE TABLE bookmarks (
                            id integer PRIMARY KEY,
                            article_id integer UNIQUE NOT NULL,
                            created_at text
                        ); """)

    @staticmethod
    def _fetchone_from_articles_where_name(conn, article_name):
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM articles WHERE name=?; """, (article_name,))
        return cur.fetchone()

    @staticmethod
    def _insert_into_bookmarks(conn, values):
        cur = conn.cursor()
        cur.execute(""" INSERT INTO bookmarks (article_id, created_at) VALUES (?, ?); """, values)
        return cur.lastrowid
