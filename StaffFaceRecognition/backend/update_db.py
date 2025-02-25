# from fastapi import FastAPI
# from pydantic import BaseModel
# import os
# import json
# from collections import defaultdict
# from facenet_pytorch import MTCNN, InceptionResnetV1
# import torch
# from PIL import Image
# import uvicorn
#
# app = FastAPI()
#
#
# class EmbeddingRequest(BaseModel):
#     db_path: str
#     output_file: str = "backend/face_embeddings.json"
#
#
# def store_embeddings(db_path, output_file):
#     if not os.path.exists(db_path):
#         return {"error": "Dataset path does not exist"}
#
#     existing_embeddings = {}
#     if os.path.exists(output_file):
#         with open(output_file, 'r') as f:
#             existing_embeddings = json.load(f)
#
#     embeddings = defaultdict(list, existing_embeddings)
#
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     mtcnn = MTCNN(image_size=160, margin=0, keep_all=False, device=device)
#     resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
#
#     for identity in os.listdir(db_path):
#         identity_path = os.path.join(db_path, identity)
#         if os.path.isdir(identity_path):
#             for image_name in os.listdir(identity_path):
#                 image_path = os.path.join(identity_path, image_name)
#                 try:
#                     img = Image.open(image_path).convert('RGB')
#                     img_cropped = mtcnn(img)
#                     if img_cropped is not None:
#                         img_embedding = resnet(img_cropped.unsqueeze(0).to(device)).detach().cpu().numpy().tolist()
#                         embeddings[identity].append(img_embedding)
#                 except Exception as e:
#                     print(f"Error processing {image_path}: {str(e)}")
#                     continue
#
#     with open(output_file, "w") as f:
#         json.dump(dict(embeddings), f, indent=4)
#
#     return {"message": "Embeddings stored successfully", "output_file": output_file}
#
#
# @app.post("/store_embeddings/")
# def api_store_embeddings(request: EmbeddingRequest):
#     return store_embeddings(request.db_path, request.output_file)
#
#
# @app.get("/load_embeddings/")
# def load_embeddings(input_file: str = "backend/face_embeddings.json"):
#     if not os.path.exists(input_file):
#         return {"error": "Embeddings file not found"}
#
#     with open(input_file, "r") as f:
#         embeddings = json.load(f)
#     return embeddings
#
# if __name__ == '__main__':
#     # Start the FastAPI server
#     uvicorn.run(app, host="0.0.0.0", port=7000)

from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import os
from collections import defaultdict
import json
from PIL import Image


def store_embeddings(db_path, output_file="face_embeddings.json"):
    # Load existing embeddings if file exists
    existing_embeddings = {}
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_embeddings = json.load(f)

    # Convert existing embeddings to defaultdict to handle new identities
    embeddings = defaultdict(list, existing_embeddings)

    # Setup device and models
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mtcnn = MTCNN(image_size=160, margin=0, keep_all=False, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

    # Process images for each identity
    for identity in os.listdir(db_path):
        identity_path = os.path.join(db_path, identity)
        if os.path.isdir(identity_path):
            # Get list of already processed images for this identity
            existing_embeddings_count = len(embeddings[identity])
            processed_images = set()

            # Process new images
            for image_name in os.listdir(identity_path):
                image_path = os.path.join(identity_path, image_name)

                # Skip if image was already processed (assuming one embedding per image)
                if len(embeddings[identity]) > 0 and image_name in processed_images:
                    continue

                try:
                    img = Image.open(image_path).convert('RGB')
                    img_cropped = mtcnn(img)

                    if img_cropped is not None:
                        img_embedding = resnet(img_cropped.unsqueeze(0).to(device)).detach().cpu().numpy().tolist()
                        embeddings[identity].append(img_embedding)
                        processed_images.add(image_name)
                except Exception as e:
                    print(f"Error processing {image_path}: {str(e)}")
                    continue

            # Print summary for this identity
            new_embeddings_count = len(embeddings[identity]) - existing_embeddings_count
            print(f"Identity: {identity}")
            print(f"  - Previous embeddings: {existing_embeddings_count}")
            print(f"  - New embeddings added: {new_embeddings_count}")
            print(f"  - Total embeddings: {len(embeddings[identity])}")

    # Save updated embeddings
    with open(output_file, "w") as f:
        json.dump(dict(embeddings), f, indent=4)
    # print(f"\nEmbeddings saved to {output_file}")


def load_embeddings(input_file="face_embeddings.json"):
    with open(input_file, "r") as f:
        embeddings = json.load(f)
    return embeddings


if __name__ == "__main__":
    db_path = "dataset"
    store_embeddings(db_path)
    embeddings = load_embeddings()
    # print("Loaded embeddings:", embeddings)