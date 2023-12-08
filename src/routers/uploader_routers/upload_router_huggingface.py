from fastapi import APIRouter
from fastapi import File, Query, UploadFile

from uploaders.hugging_face_uploader import handle_upload
from routers.uploader_router import UploaderRouter


class UploadRouterHuggingface(UploaderRouter):
    def create(self, url_prefix: str) -> APIRouter:
        router = super().create(url_prefix)

        @router.post(url_prefix + "/upload/datasets/{identifier}/huggingface", tags=["upload"])
        def huggingFaceUpload(
            identifier: int,
            file: UploadFile = File(
                ..., title="File", description="This file will be uploaded to HuggingFace"
            ),
            token: str = Query(
                ..., title="Huggingface Token", description="The access token of HuggingFace"
            ),
            username: str = Query(
                ..., title="Huggingface username", description="The username of HuggingFace"
            ),
        ) -> int:
            return handle_upload(identifier, file, token, username)

        return router
