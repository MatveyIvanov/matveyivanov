from pydantic import BaseModel


class GitHubRepository(BaseModel, extra="allow"):  # type:ignore[call-arg]
    name: str


class GitHubSender(BaseModel, extra="allow"):  # type:ignore[call-arg]
    login: str


class GitHubCreateHook(BaseModel, extra="allow"):  # type:ignore[call-arg]
    ref: str
    ref_type: str
    master_branch: str
    description: str | None
    pusher_type: str
    repository: GitHubRepository
    sender: GitHubSender
