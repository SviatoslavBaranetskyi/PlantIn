import torch


class EmbeddingService:
    def __init__(self):
        self.model = None

    def encode(self, image: torch.Tensor) -> list[float]:
        raise NotImplementedError("Will be implemented in next commit")