# coding=utf-8
import os

from ..xml import article_xml_tree


class Asset:

    def __init__(self, filename, asset_node):
        self.original_href = os.path.basename(filename)
        self.filename = filename
        self.asset_node = asset_node
        self.article_id = None

    def get_content(self):
        record = {}
        record['article_id'] = self.article_id
        record['filename'] = self.filename
        record['file'] = self.file
        record['node'] = self.asset_node
        record['location'] = self.href
        record['original_href'] = self.original_href
        return record

    @property
    def name(self):
        return self.original_href

    @property
    def file(self):
        if os.path.isfile(self.filename):
            return open(self.filename)

    @property
    def href(self):
        return self.asset_node.href

    def update_href(self, href):
        self.asset_node.update_href(href)


class Article:

    def __init__(self, xml_filename, files):
        self.basename = os.path.basename(xml_filename)
        self.filename = xml_filename
        self.article_xml_tree = article_xml_tree.ArticleXMLTree(xml_filename)
        self.files = files
        self.assets = None
        self.location = None

    def get_content(self, asset_id_items=None):
        content = {}
        content['location'] = self.location
        content['filename'] = self.filename
        content['basename'] = self.basename
        content['xml_content'] = self.content
        content['assets'] = asset_id_items
        return content

    def link_files_to_assets(self):
        if self.article_xml_tree.asset_nodes is not None:
            self.assets = {}
            self.unlinked_assets = list(
                [os.path.basename(f) for f in self.files])
            self.unlinked_files = []

            for f in self.files:
                fname = os.path.basename(f)
                asset_node = self.article_xml_tree.asset_nodes.get(fname)
                if asset_node is None:
                    self.unlinked_files.append(fname)
                else:
                    self.unlinked_assets.remove(fname)
                    self.assets[fname] = Asset(
                        f, asset_node)

    def update_href(self, asset_id_items):
        if self.assets is not None:
            for name, asset in self.assets.items():
                self.assets[name].update_href(asset_id_items[name])

    @property
    def content(self):
        return self.article_xml_tree.content
