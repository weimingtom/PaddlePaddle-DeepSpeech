# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import codecs
import functools
import wave

import soundfile
import json
import argparse
from utils.utility import add_arguments, print_arguments

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
parser.add_argument("--annotation_path",
                    default="./dataset/annotation/",
                    type=str,
                    help="Sound annotation text save path. (default: %(default)s)")
parser.add_argument("--manifest_prefix",
                    default="./dataset/",
                    type=str,
                    help="Filepath prefix for output manifests. (default: %(default)s)")
args = parser.parse_args()


def create_manifest(annotation_path, manifest_path_prefix):
    json_lines = []
    durations = []
    for annotation_text in os.listdir(annotation_path):
        print('The %s manifest takes a long time to create. Please wait ...' % annotation_text)
        annotation_text = os.path.join(annotation_path, annotation_text)
        with codecs.open(annotation_text, 'r', 'utf-8') as f:
            lines = f.readlines()
        for line in lines:
            audio_path = line.split('\t')[0]

            try:
                text = is_ustr(line.split('\t')[1].replace('\n', '').replace('\r', ''))
                audio_data, samplerate = soundfile.read(audio_path)
                duration = float(len(audio_data) / samplerate)
                durations.append(duration)
                json_lines.append(
                    json.dumps(
                        {
                            'audio_filepath': audio_path,
                            'duration': duration,
                            'text': text
                        },
                        ensure_ascii=False))
            except:
                continue

    f_train = codecs.open(os.path.join(manifest_path_prefix, 'manifest.train'), 'w', 'utf-8')
    f_dev = codecs.open(os.path.join(manifest_path_prefix, 'manifest.dev'), 'w', 'utf-8')
    f_test = codecs.open(os.path.join(manifest_path_prefix, 'manifest.test'), 'w', 'utf-8')
    for i, line in enumerate(json_lines):
        if i % 500 == 0:
            f_dev.write(line + '\n')
            f_test.write(line + '\n')
        else:
            f_train.write(line + '\n')
    f_train.close()
    f_dev.close()
    f_test.close()
    print("Create manifest done. All audio for [%d] hours!" % int(sum(durations) / 3600))


def is_ustr(in_str):
    out_str = ''
    for i in range(len(in_str)):
        if is_uchar(in_str[i]):
            out_str = out_str + in_str[i]
        else:
            out_str = out_str + ' '
    return ''.join(out_str.split())


def is_uchar(uchar):
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    if u'\u0030' <= uchar <= u'\u0039':
        return False
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return False
    if uchar in ('-', ',', '.', '>', '?'):
        return False
    return False


# 改变音频的帧率为16000Hz
def change_audio_rate(annotation_path):
    for annotation_text in os.listdir(annotation_path):
        print('The %s manifest takes a long time to create. Please wait ...' % annotation_text)
        annotation_text = os.path.join(annotation_path, annotation_text)
        with codecs.open(annotation_text, 'r', 'utf-8') as f:
            lines = f.readlines()
        for line in lines:
            audio_path = line.split('\t')[0]
            sndfile = soundfile.SoundFile(audio_path)
            samplerate = sndfile.samplerate
            if samplerate != 16000:
                f = wave.open(audio_path, "rb")
                str_data = f.readframes(f.getnframes())
                f.close()
                file = wave.open(audio_path, 'wb')
                file.setnchannels(1)
                file.setsampwidth(4)
                file.setframerate(16000)
                file.writeframes(str_data)
                file.close()


# 生成噪声的数据列表
def create_noise(path='dataset/audio/noise'):
    json_lines = []
    for file in os.listdir(path):
        audio_path = os.path.join(path, file)
        try:
            text = ""
            audio_data, samplerate = soundfile.read(audio_path)
            duration = float(len(audio_data) / samplerate)
            json_lines.append(
                json.dumps(
                    {
                        'audio_filepath': audio_path,
                        'duration': duration,
                        'text': text
                    },
                    ensure_ascii=False))
        except:
            continue
    with codecs.open(os.path.join(args.manifest_prefix, 'manifest.noise'), 'w', 'utf-8') as f_noise:
        for json_line in json_lines:
            f_noise.write(json_line + '\n')


def main():
    print_arguments(args)
    create_manifest(annotation_path=args.annotation_path,
                    manifest_path_prefix=args.manifest_prefix)


if __name__ == '__main__':
    # 改变音频的帧率为16000Hz
    # change_audio_rate(args.annotation_path)
    # 生成噪声的数据列表
    # create_noise()
    # 生成训练数据列表
    main()
