import os
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from typing import Any

import yaml

__all__ = ["make_parser", "check_args", "CliArgs"]


class WeakParser(ArgumentParser):
    def with_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["default"] = None
        super().add_argument(*args, **kwargs)
        return self

    def with_path_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["metavar"] = "P"
        kwargs["type"] = str
        return self.with_argument(*args, **kwargs)

    def with_int_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["metavar"] = "N"
        kwargs["type"] = int
        return self.with_argument(*args, **kwargs)

    def with_str_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["metavar"] = "S"
        kwargs["type"] = str
        return self.with_argument(*args, **kwargs)

    def with_store_true_argument(self, *args: Any, **kwargs: Any) -> "WeakParser":
        kwargs["action"] = "store_true"
        return self.with_argument(*args, **kwargs)


@dataclass
class CliArgs:
    config: str = os.path.join("assets", "cfg", "config.yml")
    cpu_offload: bool = False
    debug: bool = False
    no_warmup: bool = False

    model: str = None
    lora_weights: str = None
    refiner: str = None
    fp: int = 16

    def load_yml(self):
        # get default values from config file
        with open(self.config, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            self.cpu_offload = data.get("cpu_offload", self.cpu_offload)
            self.debug = data.get("debug", self.debug)
            self.no_warmup = data.get("no_warmup", self.no_warmup)
            self.model = data.get("model", self.model)
            self.lora_weights = data.get("lora_weights", self.lora_weights)
            self.refiner = data.get("refiner", self.refiner)
            self.fp = data.get("fp", self.fp)


def make_parser() -> WeakParser:
    defaults = CliArgs()
    parser = WeakParser(
        description="PixelIA - Image creation and processing Discord bot",
        epilog="For more information, visit <https://github.com/ThomasByr/pixelia>.",
    )

    return (
        parser.with_path_argument(
            "-c",
            "--config",
            dest="config",
            help=f"Path to the configuration file (default: {defaults.config}).",
        )
        .with_store_true_argument(
            "-cpu",
            "--cpu-offload",
            dest="cpu_offload",
            help="Run the program with CPU offload "
            "(local models only: lower vRAM usage but slower inference).",
        )
        .with_store_true_argument(
            "-d",
            "--debug",
            dest="debug",
            help="Run the program in debug mode.",
        )
        .with_store_true_argument(
            "--no-warmup",
            dest="no_warmup",
            help="Do not warm up the diffusion model (useful for fast debugging).",
        )
        .with_str_argument(
            "-m",
            "--model",
            dest="model",
            help="Hugging Face model name (incompatible with --endpoint).",
        )
        .with_argument(
            "-w",
            "--weights",
            dest="lora_weights",
            help="Path (or Name) to the LoRA weights file.",
        )
        .with_str_argument(
            "-r",
            "--refiner",
            dest="refiner",
            help="Hugging Face refiner model name.",
        )
        .with_int_argument(
            "--fp",
            dest="fp",
            help="Number of fixed point bits for the model (default: 16).",
        )
    )


def check_path(path: str, mode: str = "r") -> str:
    """Check if the path exists and returns it if it does."""
    try:
        with open(path, mode, encoding="utf-8"):
            return path
    except FileNotFoundError as e:
        raise ValueError(f"file {path} does not exist") from e
    except PermissionError as e:
        raise ValueError(f"file {path} is not can not be opened in [{mode}] mode") from e
    except IsADirectoryError as e:
        raise ValueError(f"file {path} is a directory") from e
    except OSError as e:
        raise ValueError(f"file {path} is not a file") from e
    except Exception as e:
        raise ValueError(f"unknown error with file {path}") from e


def check_dir(path: str) -> str:
    """Check if the directory exists and returns it if it does."""
    if os.path.isdir(path):
        return path
    raise ValueError(f"directory {path} does not exist")


def check_args(args: Namespace) -> CliArgs:
    cli_args = CliArgs()

    # check config
    if args.config:
        cli_args.config = check_path(args.config)
    cli_args.load_yml()

    # check attention slicing
    if args.cpu_offload:
        cli_args.cpu_offload = True

    # check debug
    if args.debug:
        cli_args.debug = True

    # check no warmup
    if args.no_warmup:
        cli_args.no_warmup = True

    # check model
    if args.model:
        cli_args.model = args.model

    # check weights
    if args.lora_weights:
        cli_args.lora_weights = check_path(args.lora_weights)

    # check refiner
    if args.refiner:
        cli_args.refiner = args.refiner

    # check fixed point
    if args.fp:
        if args.fp not in {16, 32}:
            raise ValueError("fixed point bits must be 16 or 32")
        cli_args.fp = args.fp

    # model needs to be set
    if cli_args.model is None:
        raise ValueError("model needs to be set (either with --model or in the config file)")

    return cli_args
