from pydantic import BaseModel


class GitHubRepository(BaseModel, extra="allow"):
    name: str


class GitHubSender(BaseModel, extra="allow"):
    login: str


class GitHubCreateHook(BaseModel, extra="allow"):
    ref: str
    ref_type: str
    master_branch: str
    description: str | None
    pusher_type: str
    repository: GitHubRepository
    sender: GitHubSender
