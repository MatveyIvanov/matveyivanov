import os
from datetime import datetime
from typing import Tuple

from dateutil.relativedelta import relativedelta

from schemas.book import Book
from schemas.experience import Experience
from schemas.project import Project
from schemas.python import Python
from schemas.stack import Stack

STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STATIC_PATH = os.environ.get("STATIC_PATH", "")

DB_USER: str = os.environ.get("DB_USER", "")
DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
DB_NAME: str = os.environ.get("DB_NAME", "")
DB_HOST: str = os.environ.get("DB_HOST", "")
DB_PORT: str = os.environ.get("DB_PORT", "")
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

TIMEZONE = os.environ.get("TIMEZONE")

DEBUG = bool(int(os.environ.get("DEBUG", 0)))
PROD = bool(int(os.environ.get("PROD", 1)))

LOGGING_MAX_BYTES = int(os.environ.get("LOGGING_MAX_BYTES", 1024 * 3))
LOGGING_BACKUP_COUNT = int(os.environ.get("LOGGING_BACKUP_COUNT", 1))
LOGGING_LOGGERS = os.environ.get("LOGGING_LOGGERS", "").split(",")
LOGGING_SENSITIVE_FIELDS = os.environ.get("LOGGING_SENSITIVE_FIELDS", "").split(",")
LOGGING_PATH = "/logs/"

PORT = os.environ.get("PORT")
ABSOLUTE_URL = os.environ.get("ABSOLUTE_URL", f"http://localhost:{PORT}")

BIRTH_DATE = datetime(2001, 3, 25)

HOME: Tuple[str] = (
    "Hello, my name is Matvey Ivanov",
    f"I'm {relativedelta(datetime.now(), BIRTH_DATE).years} y.o.",
    "Currently living in Saint-Petersburg",
    "Full-time middle Python backend developer",
)
EXPERIENCE = [
    Experience(
        place="Yandex",
        from_="2025",
        to_="today",
        description="Software Developer",
    ),
    Experience(
        place="Sixhands",
        from_="2024",
        to_="2025",
        description="Middle Python Backend Developer",
    ),
    Experience(
        place="Sixhands",
        from_="2022",
        to_="2024",
        description="Junior Python Backend Developer",
    ),
    Experience(
        place="LETI University",
        from_="2019",
        to_="2023",
        description="Bachelor in Computer Science",
    ),
]
STACK = [
    Stack(name="Python", progress="90%"),
    Stack(name="git", progress="90%"),
    Stack(name="Docker", progress="90%"),
    Stack(name="RabbitMQ", progress="75%"),
    Stack(name="Nginx", progress="75%"),
    Stack(name="PostgreSQL", progress="75%"),
    Stack(name="Redis", progress="75%"),
    Stack(name="Linux", progress="75%"),
    Stack(name="Grafana", progress="60%"),
    Stack(name="Prometheus", progress="60%"),
    Stack(name="CI/CD", progress="50%"),
    Stack(name="ffmpeg", progress="40%"),
    Stack(name="Jaeger", progress="20%"),
    Stack(name="MongoDB", progress="20%"),
    Stack(name="Cassandra", progress="20%"),
    Stack(name="Apache Kafka", progress="20%"),
    Stack(name="C++", progress="15%"),
]
PYTHON = [
    Python(name="Django", progress="90%"),
    Python(name="DRF", progress="90%"),
    Python(name="FastAPI", progress="65%"),
    Python(name="SQLAlchemy", progress="65%"),
    Python(name="Celery", progress="90%"),
    Python(name="SQLAlchemy", progress="65%"),
    Python(name="Alembic", progress="65%"),
    Python(name="Pytest", progress="90%"),
    Python(name="Flake8", progress="90%"),
    Python(name="MyPy", progress="70%"),
    Python(name="Asyncio", progress="65%"),
    Python(name="OpenCV", progress="55%"),
    Python(name="Pillow", progress="70%"),
    Python(name="QuixStreams", progress="20%"),
    Python(name="FastStream", progress="20%"),
    Python(name="NumPy", progress="20%"),
    Python(name="Matplotlib", progress="20%"),
    Python(name="requests/httpx", progress="90%"),
    Python(name="Pygame", progress="45%"),
    Python(name="SciPy", progress="10%"),
    Python(name="Flask", progress="20%"),
    Python(name="OpenTelemetry", progress="40%"),
    Python(name="Black", progress="90%"),
    Python(name="Redis", progress="90%"),
    Python(name="PyQT", progress="30%"),
    Python(name="MoviePy", progress="60%"),
    Python(name="Poetry", progress="90%"),
]
WORK_BOOKS = [
    Book(name="Grokking Algorithms by Aditya Y. Bhargava"),
    Book(name="Architecture Patterns with Python by Harry Percival and Bob Gregory"),
    Book(name="Django Design Patterns and Best Practices by Arun Ravindran"),
    Book(
        name=(
            "Building Event-Driven Microservices: "
            "Leveraging Organizational Data at Scale by Adam Bellemare"
        )
    ),
    Book(name="Monolith to Microservices by Sam Newman"),
]
OFF_WORK_BOOKS = [
    Book(name="The Witcher series of novels by Andrzej Sapkowski"),
    Book(name="Dune by Frank Herbert"),
    Book(name="The Brothers Karamazov by Fyodor Dostoevsky"),
]
PROJECTS = [
    Project(
        name="Present website",
        description="Personal website with work experience, stack, projects and more.",
        url="https://github.com/MatveyIvanov/matveyivanov",
    ),
    Project(
        name="eventscore",
        description=(
            "Open-source Python package that allows to build "
            "event-driven monolith backend applications "
            "using same architecture patterns and semantics "
            "as microservices."
        ),
        url="https://github.com/MatveyIvanov/eventscore",
    ),
    Project(
        name="dbrepos",
        description=(
            "My first open-source package that helps "
            "to work with databases via repository pattern abstraction "
            "using standardized interface."
        ),
        url="https://github.com/MatveyIvanov/dbrepos",
    ),
    Project(
        name="File upload microservice",
        description=(
            "This was a test task for job appliance, "
            "but still one of the latest open source "
            "repository with my current code-style."
        ),
        url="https://github.com/MatveyIvanov/file-upload-microservice",
    ),
    Project(
        name="DNS-client cli",
        description=(
            "Simple cli working as DNS client. "
            "You can lookup for domain names and get their IP's."
        ),
        url="https://github.com/MatveyIvanov/DNS-Client",
    ),
    Project(
        name="Huffman archiver",
        description=(
            "University project written in C++ that allows "
            "to compress text with a compression ratio up to 2 units."
        ),
        url="https://github.com/MatveyIvanov/HuffmanArchiver",
    ),
    Project(
        name="Web templates",
        description=(
            "Group of repositories containing multiple templates "
            "for some common web apps that I build."
        ),
        url="https://github.com/orgs/Python-Backend-Templates/repositories",
    ),
    Project(
        name="2 grpc microservices with API Gateway",
        description=(
            "This was a learning-purpose project, "
            "as I was trying to understand how to "
            "build microservices based on gRPC communication."
        ),
        url="https://github.com/orgs/VerimApp/repositories",
    ),
]
