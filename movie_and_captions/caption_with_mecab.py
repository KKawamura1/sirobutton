from typing import Union, Optional, List
from pathlib import Path
from logging import getLogger, Logger
import pickle
from tqdm import tqdm
import MeCab
import jaconv
import re

from movie_and_captions.models import Caption, AugmentedCaption
from movie_and_captions.data import Data


class CaptionWithMecab:
    def __init__(
            self,
            logger: Logger = getLogger(__name__)
    ) -> None:
        self._logger = logger
        self._mecab_yomi = MeCab.Tagger('-Oyomi')
        self._mecab_tagger = MeCab.Tagger()
        # bad know-how to prevent UnicodeDecodeError
        # see: https://qiita.com/kasajei/items/0805b433f363f1dba785
        self._mecab_yomi.parse('')
        self._mecab_tagger.parse('')
        # match with the strings that starts and ends with one of the remove / save parens
        parens_map = dict(removing=[('\(', '\)'), ('（', '）'), ('<', '>')],
                          saving=[('「', '」'), ('\'', '\''), ('"', '"')])
        parens_lefts_rights = {key: [''.join([paren[i] for paren in parens]) for i in range(2)]
                               for key, parens in parens_map.items()}
        regexps = {key: (fr'[{parens[0]}]([^{parens[0]}{parens[1]}]*)[{parens[1]}]')
                   for key, parens in parens_lefts_rights.items()}
        self._removing_parens_regex = re.compile(regexps['removing'])
        self._saving_parens_regex = re.compile(regexps['saving'])
        self._short_title_length_range = dict(min=12, max=28)
        # see: http://miner.hatenablog.com/entry/323
        self._not_selfstanding_poses = set([
            11,  # あ'ったらしい'
            12,  # 使い'づらい'
            17,  # そう'かしら'
            19,  # 思い'けむ'
            22,  # A'か'B
            23,  # A'とか'B
            25,  # 思い'ます'
            32, 33,  # 行って'しまう'
            50, 51, 52, 53, 54, 55, 56, 57, 58, 59,  # 接尾名詞
        ])
        self._not_ending_poses = set([
            27, 28, 29, 30,  # 接続系接頭詞
            62, 63, 64, 65, 66, 67,  # 非自立語幹
        ])

    def augment_caption(self, caption: Caption) -> Optional[AugmentedCaption]:
        # remove parentheses
        text = caption.content
        text = text.replace('\n', '')
        while True:
            # search minimal parenthesis pair
            match = self._removing_parens_regex.search(text)
            if match is None:
                break
            text = text[:match.start()] + text[match.end():]
            if len(text) == 0:
                return None
        # save parenthesis
        match = self._saving_parens_regex.search(text)
        if match is not None:
            text_candidate = match.group(1)
            # take larger one
            # ex. 'シロ「こんにちは！」' -> 'こんにちは！'
            # ex. '最高に「ハイ！」ってやつだ' -> (same as before)
            if len(text_candidate) >= len(text) / 2:
                text = text_candidate
        if len(text) == 0:
            return None
        # get yomi
        yomi_katakana = self._mecab_yomi.parse(text).strip()
        yomi = jaconv.kata2hira(yomi_katakana)
        # make short title
        if len(text) <= self._short_title_length_range['min']:
            short_title = text
        else:
            mecab_node = self._mecab_tagger.parseToNode(text).next
            text_ends = 0
            previous_continuous_flag = False
            while mecab_node is not None and mecab_node.next is not None:
                check_length = True
                feature_posid = mecab_node.posid
                # if the pos tag is not self-standing one (自立語), continue
                if feature_posid in self._not_selfstanding_poses:
                    check_length = False
                # if the previous tag is continuous one (継続語), continue
                if previous_continuous_flag:
                    previous_continuous_flag = False
                    check_length = False
                if feature_posid in self._not_ending_poses:
                    previous_continuous_flag = True
                # check length
                text_ends_will_be = text_ends + len(mecab_node.surface)
                if check_length and text_ends_will_be >= self._short_title_length_range['min']:
                    break
                if text_ends_will_be >= self._short_title_length_range['max']:
                    break
                text_ends = text_ends_will_be
                mecab_node = mecab_node.next
            short_title = text[:text_ends]
        augmented_caption = AugmentedCaption(short_title=short_title, yomi=yomi,
                                             **caption._asdict())
        if len(short_title) < len(caption.content):
            self._logger.debug('convert {} to {}'.format(caption.content, short_title))
        return augmented_caption

    def do(
            self,
            old_data: Data
    ) -> Data:
        new_data = []
        for i, video_datum in enumerate(tqdm(old_data)):
            caption_asdicts = video_datum['captions']
            captions: List[Caption] = [Caption(**caption_asdict)
                                       for caption_asdict in caption_asdicts]
            augmented_caption_asdicts = []
            for caption in captions:
                augmented_caption = self.augment_caption(caption)
                if augmented_caption is not None:
                    augmented_caption_asdicts.append(augmented_caption._asdict())
            new_data_dict = dict(**video_datum)
            new_data_dict['augmented_captions'] = augmented_caption_asdicts
            new_data.append(new_data_dict)
        return new_data
