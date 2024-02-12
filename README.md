# pixelia - Image creation and processing Discord bot

[![GitHub license](https://img.shields.io/github/license/ThomasByr/pixelia)](https://github.com/ThomasByr/pixelia/blob/master/LICENSE)
[![GitHub commits](https://badgen.net/github/commits/ThomasByr/pixelia)](https://GitHub.com/ThomasByr/pixelia/commit/)
[![GitHub latest commit](https://badgen.net/github/last-commit/ThomasByr/pixelia)](https://gitHub.com/ThomasByr/pixelia/commit/)
[![Maintenance](https://img.shields.io/badge/maintained%3F-yes-green.svg)](https://GitHub.com/ThomasByr/pixelia/graphs/commit-activity)

[![GitHub release](https://img.shields.io/github/release/ThomasByr/pixelia)](https://github.com/ThomasByr/pixelia/releases/)
[![Author](https://img.shields.io/badge/author-@ThomasByr-blue)](https://github.com/ThomasByr)
[![Author](https://img.shields.io/badge/author-@ThomasD-blue)](https://github.com/LosKeeper)

1. [✏️ Setup](#️-setup)
2. [👩‍🏫 Usage](#-usage)
3. [🧑‍🏫 Contributing](#-contributing)
4. [⚖️ License](#️-license)
5. [🔄 Changelog](#-changelog)
6. [🐛 Bugs and TODO](#-bugs-and-todo)
7. [🎨 Logo and Icons](#-logo-and-icons)

## ✏️ Setup

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/info.svg">
>   <img alt="Info" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/info.svg">
> </picture><br>
>
> Please note we do not officially support Windows or MacOS, but we do provide some instructions for those who want to use it on these platforms.

You do not explicitly need a conda environment for the bot to run. But it is always recommended nontheless, especially because the next LTS of Ubuntu won't let users pip-install anything without a virtual environment. At the time of writing, this app `python >= 3.11` to run.

```bash
git clone git@github.com:ThomasByr/pixelia.git
cd pixelia
```

You can create and activate a conda environment with the following commands :

```bash
conda env create -f environment.yml -y
conda activate pixelia
# alternatively, you can just use pip
# pip install --upgrade -r requirements.txt
```

Finally, run the discord bot with :

```bash
python pixelia.py
```

## 👩‍🏫 Usage

## 🧑‍🏫 Contributing

If you ever want to contribute, either request the contributor status, or, more manually, fork the repo and make a pull request !

We are using [black](https://github.com/psf/black) to format the code, so make sure you have it installed and run :

```ps1
black .
```

> The standard procedure is :
>
> ```txt
> fork -> git branch -> push -> pull request
> ```
>
> Note that we won't accept any PR :
>
> - that does not follow our Contributing Guidelines
> - that is not sufficiently commented or isn't well formated
> - without any proper test suite
> - with a failing or incomplete test suite

Happy coding ! 🙂

## ⚖️ License

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/warning.svg">
>   <img alt="Warning" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/warning.svg">
> </picture><br>
>
> Working source code is licensed under AGPL, the rest is unlicensed. If you whish not to use source code, please use the license of your choice. The following license only applies to the code itself and is not legal advice. <FONT COLOR="#ff0000"><u>The license of this repo does not apply to the resources used in it.</u></FONT> Please check the license of each resource before using them.

This project is licensed under the AGPL-3.0 new or revised license. Please read the [LICENSE](LICENSE.md) file. Additionally :

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

- Neither the name of the pixelia authors nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

```LICENSE
pixelia - Image creation and processing Discord bot
Copyright (C) 2024-present Thomas BOUYER & Thomas DUMOND

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
```

## 🔄 Changelog

Please read the [changelog](changelog.md) file for the full history !

<details>
  <summary> </summary>

</details>

## 🐛 Bugs and TODO

**TODO** (first implementation version)

- [ ] add `redo` button to /imagine commands

**Known Bugs** (latest fix)

- [ ] might want to double check /manage group logic

## 🎨 Logo and Icons

Unless otherwise stated, all icons and logos are made by the author.
Copyright (C) 2024 Thomas BOUYER, all rights reserved.

Tools used :

- [Microsoft Designer](https://designer.microsoft.com/)
- [Clip Studio Paint](https://www.clipstudio.net/en)
- [Canva](https://www.canva.com/)
