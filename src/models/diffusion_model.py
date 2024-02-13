import asyncio
import os
from threading import Lock

import torch
from diffusers import DiffusionPipeline
from PIL import Image

__all__ = ["DiffusionModel"]


class DiffusionModel:

    def __init__(
        self,
        name: str,
        refiner: str = None,
        lora_weights: str = None,
        cpu_offload: bool = False,
        fp: int = 16,
    ):
        self.name = name
        self.refiner = refiner
        self.weights = lora_weights
        self.cpu_offload = cpu_offload

        variant = "fp16" if fp == 16 else "fp32"
        torch_type = torch.float16 if fp == 16 else torch.float32

        self.__lock = Lock()
        self.__cuda_available = torch.cuda.is_available()
        self.__refiner = None
        self.__base = DiffusionPipeline.from_pretrained(
            self.name, torch_dtype=torch_type, variant=variant, use_safetensors=True
        )
        if self.weights is not None:
            self.__base.load_lora_weights(self.weights)
        if self.__cuda_available:
            if self.cpu_offload:
                self.__base.enable_model_cpu_offload()
            else:
                self.__base.to("cuda")
        if os.name != "nt":
            self.__base.unet = torch.compile(self.__base.unet, mode="reduce-overhead", fullgraph=True)
        self.__base.safety_checker = lambda images, **kwargs: (images, [False] * len(images))
        if self.refiner is not None:
            self.__refiner = DiffusionPipeline.from_pretrained(
                self.refiner,
                text_encoder_2=self.__base.text_encoder_2,
                vae=self.__base.vae,
                torch_dtype=torch_type,
                use_safetensors=True,
                variant=variant,
            )
            if self.__cuda_available:
                if self.cpu_offload:
                    self.__refiner.enable_model_cpu_offload()
                else:
                    self.__refiner.to("cuda")
            if os.name != "nt":
                self.__refiner.unet = torch.compile(
                    self.__refiner.unet, mode="reduce-overhead", fullgraph=True
                )
            self.__refiner.safety_checker = lambda images, **kwargs: (images, [False] * len(images))

        self.__n_steps = 40
        self.__high_noise_frac = 0.8

    def __generate(self, pprompt: str, nprompt: str = None) -> Image.Image:
        images = None
        match self.refiner:
            case None:
                with self.__lock:
                    images = self.__base(prompt=pprompt, negative_prompt=nprompt).images
            case str(_):
                with self.__lock:
                    images = self.__base(
                        prompt=pprompt,
                        negative_prompt=nprompt,
                        num_inference_steps=self.__n_steps,
                        denoising_end=self.__high_noise_frac,
                        output_type="latent",
                    ).images
                    images = self.__refiner(
                        prompt=nprompt,
                        negative_prompt=nprompt,
                        num_inference_steps=self.__n_steps,
                        denoising_start=self.__high_noise_frac,
                        image=images,
                    ).images
            case _:
                raise ValueError("Refiner must be a string or None")

        return images[0]

    async def query(self, pprompt: str, nprompt: str = None) -> Image.Image:
        """Query the model with a positive and negative prompt"""
        return await asyncio.to_thread(self.__generate, pprompt, nprompt)
