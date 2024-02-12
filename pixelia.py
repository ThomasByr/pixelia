#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#! PixelIA - Image creation and processing Discord bot
#!
#! Copyright (c) 2024-present, ThomasByr & ThomasD
#! AGPL-3.0-or-later (https://www.gnu.org/licenses/agpl-3.0.en.html)
#! All rights reserved.
#!
#! Redistribution and use in source and binary forms, with or without
#! modification, are permitted provided that the following conditions are met:
#!
#! * Redistributions of source code must retain the above copyright notice,
#!   this list of conditions and the following disclaimer.
#!
#! * Redistributions in binary form must reproduce the above copyright notice,
#!   this list of conditions and the following disclaimer in the documentation
#!   and/or other materials provided with the distribution.
#!
#! * Neither the name of this software's authors nor the names of its
#!   contributors may be used to endorse or promote products derived from
#!   this software without specific prior written permission.
#!
#! This program is free software: you can redistribute it and/or modify
#! it under the terms of the GNU Affero General Public License as published by
#! the Free Software Foundation, either version 3 of the License, or
#! (at your option) any later version.
#!
#! This program is distributed in the hope that it will be useful,
#! but WITHOUT ANY WARRANTY; without even the implied warranty of
#! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#! GNU Affero General Public License for more details.
#!
#! You should have received a copy of the GNU Affero General Public License
#! along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

if sys.version_info < (3, 11):
    raise RuntimeError("This program requires Python 3.11")


if __name__ == "__main__":
    import logging
    import os

    from alive_progress import config_handler
    from alive_progress.animations.bars import bar_factory
    from alive_progress.animations.spinners import frame_spinner_factory
    from dotenv import load_dotenv
    from termcolor import colored

    from src.cli import check_args, make_parser
    from src.helper.logger import init_logger

    bar = bar_factory("\u2501", borders=(" ", " "), background=" ")
    spinner = frame_spinner_factory([colored(p, "cyan") for p in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"])
    config_handler.set_global(length=40, max_cols=110, enrich_print=False, bar=bar, spinner=spinner)

    args = check_args(make_parser().parse_args())

    init_logger(logging.DEBUG if args.debug else logging.INFO)

    assert load_dotenv(), "Failed to load .env file"
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_INVITE = os.getenv("BOT_INVITE")

    from src.core import UsefulClient

    UsefulClient(args, invite=BOT_INVITE).run(BOT_TOKEN)
