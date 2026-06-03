import boto3

from backend.src.config.app_config import AgentConfig

s3_client = boto3.client("s3")


def get_file(file_name: str, agent_conf: AgentConfig):
    if agent_conf.env == "cloud":
        return s3_client.get_object(
            Bucket=agent_conf.bucket_name,
            Key=file_name
        )

    return agent_conf.local_data_dir / file_name