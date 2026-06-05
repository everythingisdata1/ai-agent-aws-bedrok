import logging
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from src.config.app_config import AgentConfig

log = logging.getLogger(__name__)

s3_client = boto3.client("s3")


class FileLoader:
    """
    Handles reading and writing conversation files from either:
    - S3 (cloud mode)
    - Local filesystem (local mode)
    """

    def __init__(self, agent_conf: AgentConfig):
        log.info("Initializing FileLoader | instance_id=%s", id(self))
        self.agent_conf = agent_conf

    @staticmethod
    def _get_file_name(session_id: str) -> str:
        return f"conversation_{session_id}.json"

    def _load_file_s3(self, file_name: str) -> str | None:
        log.info("Loading file from S3 | file=%s | env=%s", file_name, self.agent_conf.app_env, )

        try:
            response = s3_client.get_object(
                Bucket=self.agent_conf.bucket_name,
                Key=file_name,
            )

            return response["Body"].read().decode("utf-8")

        except ClientError as ex:
            log.info("File does not exist in S3 | file=%s", file_name)
            return None

    def _load_file_local(self, file_name: str) -> str | None:
        """
        Load a file from the local filesystem.
        """
        file_path = self.agent_conf.local_data_dir / file_name

        log.info("Loading local file | path=%s | env=%s", file_path, self.agent_conf.app_env, )

        if not file_path.exists():
            return None
        try:
            return file_path.read_text(encoding="utf-8")
        except OSError:
            log.exception("Failed to read local file | path=%s", file_path)
            raise

    def _save_to_s3(self, file_name: str, content: str) -> None:
        """
        Save content to S3.
        """
        log.info("Saving file to S3 | file=%s | env=%s", file_name, self.agent_conf.app_env, )

        try:
            s3_client.put_object(Bucket=self.agent_conf.bucket_name,
                                 Key=file_name, Body=content, ContentType="application/json", )

        except ClientError:
            log.exception("Failed to save file to S3 | file=%s", file_name)
            raise

    def _save_to_local(self, file_name: str, content: str) -> None:
        """
        Save content to local filesystem.
        """
        file_path: Path = self.agent_conf.local_data_dir / file_name

        log.info("Saving local file | path=%s | env=%s", file_path, self.agent_conf.app_env, )

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")

        except OSError:
            log.exception("Failed to save local file | path=%s", file_path)
            raise

    def get_file(self, session_id: str) -> str | None:
        """
        Load conversation content by session ID.
        """
        file_name = self._get_file_name(session_id)

        if self.agent_conf.app_env == "cloud":
            return self._load_file_s3(file_name)

        return self._load_file_local(file_name)

    def save(self, session_id: str, content: str) -> None:
        """
        Save conversation content by session ID.
        """
        file_name = self._get_file_name(session_id)

        if self.agent_conf.app_env == "cloud":
            self._save_to_s3(file_name, content)
        else:
            self._save_to_local(file_name, content)

    def load_by_name(self, file_name: str) -> str | None:
        if self.agent_conf.app_env == "cloud":
            return self._load_file_s3(file_name)

        return self._load_file_local(file_name)
