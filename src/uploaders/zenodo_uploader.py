import io
import json
import requests

from fastapi import UploadFile, HTTPException, status

from database.model.dataset.dataset import Dataset
from database.model.platform.platform_names import PlatformName
from database.session import DbSession
from database.validators import zenodo_validators
from uploaders.uploader import Uploader


class ZenodoUploader(Uploader):
    @property
    def base_url(self) -> str:
        return "https://zenodo.org/api/deposit/depositions"

    def __init__(self) -> None:
        super().__init__(PlatformName.zenodo, zenodo_validators.throw_error_on_invalid_identifier)

    def handle_upload(self, identifier: int, publish: bool, token: str, file: UploadFile):
        """
        Method to upload content to the Zenodo platform.
        """
        with DbSession() as session:
            dataset = self._get_resource(session, identifier)
            platform_resource_id = dataset.platform_resource_identifier
            platform_name = dataset.platform

            self._validate_patform_name(platform_name, identifier)
            self._validate_repo_id(platform_resource_id)

            metadata = self._generate_metadata(dataset)
            if platform_resource_id is None:
                current_zenodo_metadata = self._create_repo(token, metadata)
                repo_id = current_zenodo_metadata["id"]
                dataset.platform = "zenodo"
                dataset.platform_resource_identifier = f"zenodo.org:{repo_id}"
            else:
                repo_id = platform_resource_id.split(":")[-1]
                current_zenodo_metadata = self._get_metadata_from_zenodo(repo_id, token)

                if current_zenodo_metadata["state"] == "done":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "This resource is already public and "
                            "can't be edited with this endpoint. "
                            "You can access and modify it at "
                            f"{current_zenodo_metadata['links']['record']}",
                        ),
                    )
                self._update_zenodo_metadata(repo_id, token, metadata)

            repo_url = current_zenodo_metadata["links"]["bucket"]
            self._upload_file(repo_url, token, file)

            if publish:
                new_zenodo_metadata = self._publish_resource(repo_id, token)
                record_url = new_zenodo_metadata["links"]["record"]
                distribution = self._get_distribution_from_published(record_url)
            else:
                distribution = self._get_distribution_from_draft(repo_id, token)

            self._store_resource_updated(session, dataset, *distribution, update_all=True)

            return dataset.identifier

    def _create_repo(self, token: str, metadata: dict) -> dict:
        """
        Creates an empty repo with some metadata on Zenodo.
        """
        params = {"access_token": token}
        try:
            res = requests.post(
                self.base_url,
                params=params,
                json={"metadata": metadata},
            )
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_201_CREATED:
            msg = "Error creating a new repo on zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        return res.json()

    def _get_metadata_from_zenodo(self, repo_id: str, token: str) -> dict:
        """
        Get metadata of the dataset identified by its identifier `repo_id` from Zenodo.
        """
        params = {"access_token": token}
        try:
            res = requests.get(f"{self.base_url}/{repo_id}", params=params)
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_200_OK:
            msg = "Error retrieving information from zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        return res.json()

    def _update_zenodo_metadata(self, repo_id: str, token: str, metadata: dict) -> None:
        """
        Updates the zenodo repo with some metadata.
        """
        headers = {"Content-Type": "application/json"}
        try:
            res = requests.put(
                f"{self.base_url}/{repo_id}",
                params={"access_token": token},
                data=json.dumps({"metadata": metadata}),
                headers=headers,
            )
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_200_OK:
            msg = "Error uploading metadata to zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

    def _upload_file(self, repo_url: str, token: str, file: UploadFile) -> None:
        """
        Uploads a file to zenodo using a bucket url where the files are stored.
        """
        params = {"access_token": token}
        try:
            res = requests.put(
                f"{repo_url}/{file.filename}", data=io.BufferedReader(file.file), params=params
            )
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_201_CREATED:
            msg = "Error uploading a file to zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

    def _publish_resource(self, repo_id: str, token: str) -> dict:
        """
        Publishes the dataset with all content on Zenodo.
        """
        params = {"access_token": token}
        try:
            res = requests.post(f"{self.base_url}/{repo_id}/actions/publish", params=params)
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_202_ACCEPTED:
            msg = "Error publishing the dataset on zenodo. Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        return res.json()

    def _get_distribution_from_published(self, record_url: str) -> list[dict]:
        """
        Gets metadata of the published files.
        """
        try:
            res = requests.get(f"{record_url}/files")
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_200_OK:
            msg = (
                "Error retrieving the resource files from zenodo. Zenodo api returned a http error:"
            )
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        files_metadata = res.json()["entries"]
        distribution = [
            {
                "platform": "zenodo",
                "platform_resource_identifier": file["file_id"],
                "checksum": file["checksum"],
                "content_url": file["links"]["content"],
                "content_size_kb": file["size"],
                "name": file["key"],
            }
            for file in files_metadata
        ]

        return distribution

    def _get_distribution_from_draft(self, repo_id: str, token: str) -> list[dict]:
        """
        Generates a distribution list from metadata of the files in draft retrieved from zenodo.
        """
        params = {"access_token": token}
        try:
            res = requests.get(f"{self.base_url}/{repo_id}/files", params=params)
        except Exception as exc:
            raise _wrap_exception_as_http_exception(exc)

        if res.status_code != status.HTTP_200_OK:
            msg = "Error retrieving the resource files in draft from zenodo."
            "Zenodo api returned a http error:"
            raise HTTPException(status_code=res.status_code, detail=f"{msg} {res.text}")

        files_metadata = res.json()
        distribution = [
            {
                "platform": "zenodo",
                "platform_resource_identifier": file["id"],
                "checksum": file["checksum"],
                "content_url": "",
                "content_size_kb": file["filesize"],
                "name": file["filename"],
            }
            for file in files_metadata
        ]

        return distribution

    def _generate_metadata(self, dataset: Dataset) -> dict:
        """
        Generates metadata as a dictionary based on the data from the dataset model.
        """
        metadata = {
            "title": dataset.name,
            "description": f"{dataset.description.plain if dataset.description else ''}.\n"
            "Created from AIOD platform",
            "upload_type": "dataset",
            "creators": [
                {"name": f"{creator.name}", "affiliation": ""} for creator in dataset.creator
            ],
            "keywords": [kw.name for kw in dataset.keyword],
            "method": dataset.measurement_technique or "",
            "access_right": f"{'open' if dataset.is_accessible_for_free else 'closed'}",
            # TODO: include licence in the right format.
            # "license": dataset.license.name if dataset.license else "cc-zero",
        }

        return metadata


def _wrap_exception_as_http_exception(exc: Exception):
    if isinstance(exc, HTTPException):
        return exc

    exception = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=(
            "Unexpected exception while processing your request. "
            "Please contact the maintainers: "
            f"{exc}"
        ),
    )
    return exception
