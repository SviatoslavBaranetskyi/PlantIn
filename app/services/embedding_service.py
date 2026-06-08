import torch
from PIL import Image
from torchvision.models import ResNet18_Weights, resnet18


class EmbeddingService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        weights = ResNet18_Weights.DEFAULT
        model = resnet18(weights=weights)
        self.model = torch.nn.Sequential(*list(model.children())[:-1]).to(self.device)

        self.model.eval()

        self.preprocess = weights.transforms()

    @torch.no_grad()
    def encode(self, image: Image.Image) -> list[float]:
        tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        features = self.model(tensor).flatten(1)

        features = torch.nn.functional.normalize(features, p=2, dim=1)

        return features.squeeze(0).cpu().numpy().tolist()
