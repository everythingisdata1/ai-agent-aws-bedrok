import boto3

from src.config.app_config import AgentConfig

s3_client = boto3.client("s3")
import logging

log = logging.getLogger(__name__)


def get_file(file_name: str, agent_conf: AgentConfig):
    print(f"Getting file: {file_name} | App Environment: {agent_conf.app_env}")
    log.info(f"Getting file: {file_name} | App Environment: {agent_conf.app_env}")
    if agent_conf.app_env == "cloud":
        return s3_client.get_object(
            Bucket=agent_conf.bucket_name,
            Key=file_name
        )

    return agent_conf.local_data_dir / file_name


def save_file(file_name: str, content: str, agent_conf: AgentConfig):
    log.info(f"Saving file: {file_name} | App Environment: {agent_conf.app_env}")
    print(f"Saving file: {file_name} | App Environment: {agent_conf.app_env}")
    if agent_conf.app_env == "cloud":
        s3_client.put_object(Bucket=agent_conf.bucket_name,
                             Key=file_name,
                             Body=content,
                             ContentType="application/json")
    else:
        print(f"Saving file to local path: {agent_conf.local_data_dir / file_name}")
        file_path = agent_conf.local_data_dir / file_name
        file_path.write_text(content, encoding="utf-8")
