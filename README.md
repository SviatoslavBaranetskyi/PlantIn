# Duplicate Image Detection Service

FastAPI service for uploading images, storing their vector embeddings in Qdrant,
and finding duplicate images by `request_id`.

The service uses a pretrained ResNet18 feature extractor from `torchvision`.
Each image is converted into a normalized 512-dimensional embedding and stored in
Qdrant with request metadata.

## Features

- `POST /images` accepts multiple JPEG/PNG files via `multipart/form-data`.
- `GET /duplicates/{request_id}` returns duplicate image pairs for a previous
  upload request.
- Image validation: JPEG/PNG only, max size 10 MB per image.
- Vector search backend: Qdrant.
- ML stack: PyTorch + torchvision pretrained ResNet18.
- Docker and docker-compose setup included.
- Basic API tests for upload and duplicate search.

## Tech Stack

- Python 3.12
- FastAPI
- PyTorch / torchvision
- Qdrant
- pytest
- ruff
- Docker

## Project Structure

```text
app/
  api/routes/          FastAPI route handlers
  core/                Application settings
  db/                  Qdrant client factory
  models/              Response schemas
  repositories/        Request metadata storage
  services/            Image validation, embeddings, vector search, duplicates
tests/                 API tests
Dockerfile
docker-compose.yml
```

## Quick Start With Docker

Create `.env` from the sample:

```bash
cp .env.sample .env
```

Start the service:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Qdrant dashboard:

```text
http://localhost:6333/dashboard
```

## API Usage

### Upload Images

```http
POST /images
Content-Type: multipart/form-data
```

Form field:

| Key | Type | Description |
| --- | --- | --- |
| `files` | File[] | One or more JPEG/PNG images |

Example with curl:

```bash
curl -F "files=@image-1.jpg" -F "files=@image-2.jpg" http://localhost:8000/images
```

Successful response:

```json
{
  "request_id": "37a3fc08-e5ee-49a2-a4e9-bfa4b1e0c05e",
  "uploaded": 2
}
```

Postman setup:

1. Method: `POST`
2. URL: `http://localhost:8000/images`
3. Body: `form-data`
4. Add key `files`
5. Set key type to `File`
6. Select a JPEG or PNG image
7. For multiple images, add more rows with the same key `files`


### Find Duplicates

```http
GET /duplicates/{request_id}
```

Example:

```bash
curl http://localhost:8000/duplicates/37a3fc08-e5ee-49a2-a4e9-bfa4b1e0c05e
```

Response with duplicates:

```json
{
  "request_id": "37a3fc08-e5ee-49a2-a4e9-bfa4b1e0c05e",
  "duplicates": [
    {
      "source_id": "f4d5f9f1-3eda-4d6b-9675-58ef1d46260b",
      "duplicate_id": "362f8c8a-3266-4ffb-a7b8-009cf880e11f",
      "score": 1.0,
      "source_filename": "image-1.jpg",
      "duplicate_filename": "image-2.jpg"
    }
  ],
  "message": "Duplicates found"
}
```

Response without duplicates:

```json
{
  "request_id": "37a3fc08-e5ee-49a2-a4e9-bfa4b1e0c05e",
  "duplicates": [],
  "message": "No duplicates found"
}
```

## Local Development

Install dependencies:

```bash
uv sync
```

Run the API locally:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

For local development without Docker, set Qdrant in `.env`:

```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## Tests and Linting

Run tests:

```bash
uv run pytest -q
```

Run ruff:

```bash
uv run ruff check .
```

Optional formatting:

```bash
uv run ruff format .
```

## Configuration

Environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `PROJECT_NAME` | `Duplicate Image Detection Service` | FastAPI title |
| `PROJECT_VERSION` | `1.0.0` | API version |
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant REST port |
| `QDRANT_COLLECTION` | `images` | Qdrant collection name |
| `MAX_IMAGE_SIZE_MB` | `10` | Max image size |
| `EMBEDDING_SIZE` | `512` | ResNet18 feature vector size |
| `SIMILARITY_THRESHOLD` | `0.98` | Cosine similarity threshold |

## Implementation Notes

- The service extracts embeddings from ResNet18 before the classification head,
  producing 512-dimensional feature vectors.
- Embeddings are L2-normalized and stored in Qdrant using cosine distance.
- Each Qdrant point payload contains `filename` and `request_id`.
- Duplicate search is scoped to the uploaded request using a Qdrant payload
  filter, so results for one request do not leak into another request.
- Request metadata is stored in `storage/requests.json`. For a production system,
  this should be replaced with a durable database table.

## Troubleshooting

If `POST /images` is slow on the first valid request, the pretrained model is
being initialized. Subsequent requests should be faster.

If Postman returns `422`, check that the form-data key is exactly `files` and its
type is `File`.

If the API cannot connect to Qdrant in Docker, check that `.env` contains:

```env
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```
