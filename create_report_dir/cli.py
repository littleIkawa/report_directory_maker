import os
import sys
import shutil
from typing import Union, Dict

import fire
import yaml

from .utils import detect_invalid_char, error_print
from .temp import latex_template


def get_config() -> Dict[str, Union[None, str]]:
    """コンフィグデータを取得する"""
    # 存在確認
    homedir = os.path.expanduser("~")
    config_path = os.path.join(homedir, ".texdirmakerrc")
    if not os.path.isfile(config_path):
        # 存在しない場合作成
        print("config file not found. create it?[y/N] -> ", end="")
        if input() == "y":
            with open(config_path, mode="w") as f:
                default_settings = {"preamble": None, "author": "author"}
                yaml.dump(default_settings, f)
            print(f"File '{config_path}' created. Edit it later")
            return default_settings
        else:
            print("canceled")
            sys.exit(0)
    else:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return config


def create_dir(dir_name: str, force: bool) -> str:
    """カレントディレクトリ直下にディレクトリを作成する. 作成した結果のフルパスを返す"""
    cwd = os.getcwd()
    if detect_invalid_char(dir_name):
        error_print(f"The directory name '{dir_name}' is not available.")
        sys.exit(1)
    new_full_path = os.path.normpath(os.path.join(cwd, dir_name))

    try:
        os.mkdir(new_full_path)
    except FileExistsError as e:
        # TODO: forceオプションを有効にする
        error_print(str(e))
        sys.exit(2)
    else:
        print(f"created the directory \x1b[38;5;11m'{new_full_path}'\x1b[m")

    return new_full_path


def create_file(
    dir_path: str, filename: str, title: str, author: str, preamble: Union[None, str]
):
    """ファイルを作成する. preambleはディレクトリにコピーしたいファイルの絶対パスを指定する."""
    filepath = os.path.join(dir_path, filename)
    formatted = latex_template.format(title=title, author=author)
    if preamble is None or not os.path.isfile(preamble):
        print("preamble is not found (or undefined).")
    else:
        shutil.copy2(preamble, dir_path)
    with open(filepath, mode="w") as f:
        f.write(formatted)
    print(f"created the file \x1b[38;5;11m'{filepath}'\x1b[m")


def app(
    dir_name, filename: Union[str, None] = None, force: bool = False, title: str = ""
):
    """
    指定した名前のディレクトリを作成し, その中にuplatexのレポートのテンプレートを生成する.
    設定ファイルで著者名とプリアンブルのテンプレートファイルを指定できる.
    著者名はauthorの部分に埋め込まれ, プリアンブルは作成したディレクトリにコピーされる.
    """
    config = get_config()
    preamble_path = config.get("preamble")
    author = str(config.get("author"))

    dir_name = str(dir_name)
    if filename is None:
        filename = dir_name + ".tex"
    elif detect_invalid_char(filename):
        error_print(f"The file name '{filename}' is not available.")
        sys.exit(1)
    else:
        filename += ".tex"

    new_full_path = create_dir(dir_name, force)
    create_file(new_full_path, filename, title, author, preamble_path)


def main():
    fire.Fire(app)
