# KeywordExtractor.py
# Copyright (C) 2024  Dr Horst Herb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This module provides  fast and efficient keyword extractor from text using the rake_nltk library
Rake extracts many more keywords than Yake, but Yake is faster and more concise
Yake has a keyword highlighting function for text too, not used presently"""

from rake_nltk import Rake  #pip install rake-nltk
import yake # pip install git+https://github.com/LIAAD/yake –-upgrade


def merge_lists_excluding_duplicates(list1, list2):
    return list(set(list1) | set(list2))


class YakeKeywordExtractor:
    """A class to extract keywords from a publication"""
    def __init__(self):
        self.yake = yake.KeywordExtractor()
        
    def extract_keywords(self, text: str) -> list[str]:
        """extracts keywords from the text
        :param text: the text to extract keywords from
        :return: a list of keywords
        """
        keywords = self.yake.extract_keywords(text) #returns a list of tuples (keyword, score)
        return [keyword for keyword, score in keywords] #we only want to rteurn the keywords


class RakeKeywordExtractor:
    """A class to extract keywords from a publication"""
    def __init__(self):
        try:
            self.rake=Rake(include_repeated_phrases=False, max_length=2)
        except:
            import nltk
            nltk.download('stopwords')
            self.rake=Rake()
        
    def extract_keywords(self, text: str) -> list[str]:
        """extracts keywords from the text
        :param text: the text to extract keywords from
        :return: a list of keywords
        """
        self.rake.extract_keywords_from_text(text)
        return self.rake.get_ranked_phrases()
    


class KeywordExtractor:
    """A class to extract keywords from a publication
    The class uses one or more keyword extractors to extract keywords from a publication
    If more than one extractor is used, the keywords are merged and duplicates are removed"""
  
    def __init__(self, use_extractors=['yake', 'rake']):
        """Initializes the keyword extractor
        :param use_extractors: a list of keyword extractors to use. The extractors are used in the order they are defined in the list"""
        self.extractors = []
        if 'yake' in use_extractors:
            self.extractors.append(YakeKeywordExtractor())
        if 'rake' in use_extractors:
            self.extractors.append(RakeKeywordExtractor())
        assert len(self.extractors) > 0, "No keyword extractors specified"

    def extract_keywords(self, text: str) -> list[str]:
        """extracts keywords from the text
        :param text: the text to extract keywords from
        :return: a list of keywords
        """
        keywords = []
        for extractor in self.extractors:
            keywords = merge_lists_excluding_duplicates(keywords, extractor.extract_keywords(text))
        return keywords


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Extract keywords from a text file.')
    parser.add_argument('filename', help='The name of the text file to extract keywords from')
    args = parser.parse_args()

    # Read the text from the file
    text = Path(args.filename).read_text()

    # Extract keywords
    ke = KeywordExtractor()
    print(ke.extract_keywords(text))