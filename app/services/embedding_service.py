import torch
import torchvision.transforms as T
from PIL import Image


class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = torch.hub.load(
            "pytorch/vision",
            "vit_b_32",
            pretrained=True,
        ).to(self.device)

        self.model.eval()

        self.preprocess = T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(
                    mean=[0.5, 0.5, 0.5],
                    std=[0.5, 0.5, 0.5],
                ),
            ]
        )

    @torch.no_grad()
    def encode(self, image: Image.Image) -> list[float]:
        tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        features = self.model(tensor)

        features = torch.nn.functional.normalize(features, p=2, dim=1)

        return features.squeeze(0).cpu().numpy().tolist()