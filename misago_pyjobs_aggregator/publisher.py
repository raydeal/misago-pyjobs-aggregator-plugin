from __future__ import annotations

from dataclasses import asdict

from .domain import JobAdvertisement


def format_job(job: JobAdvertisement, updated: bool = False) -> str:
    lines = [
        "### Job advertisement" if not updated else "### Job advertisement update",
        "",
    ]
    lines += [
        f"**Company:** {job.company or 'Not specified'}",
        f"**Source:** {job.url}",
    ]
    if job.locations:
        lines.append(f"**Location:** {', '.join(job.locations)}")
    if job.salary:
        lines.append(f"**Salary:** {job.salary}")
    if job.contract_time:
        lines.append(f"**Contract:** {job.contract_time}")
    if job.is_remote or job.is_hybrid:
        lines.append(f"**Work mode:** {'remote' if job.is_remote else 'hybrid'}")
    if job.skills:
        lines.append(f"**Skills:** {', '.join(job.skills)}")
    lines += [
        "",
        job.description.strip(),
        "",
        f"[View the original advertisement]({job.url})",
    ]
    return "\n".join(lines)


class MisagoPublisher:
    """Small integration seam around the Misago version-specific posting API."""

    def __init__(self, category_id: int, bot_user_id: int):
        self.category_id = category_id
        self.bot_user_id = bot_user_id

    def create_thread(self, title: str, content: str) -> int:
        from misago.categories.models import Category
        from misago.threads.posting import start_thread
        from misago.users.models import User

        thread = start_thread(
            category=Category.objects.get(pk=self.category_id),
            starter=User.objects.get(pk=self.bot_user_id),
            title=title,
            content=content,
        )
        return thread.pk

    def add_post(self, thread_id: int, content: str) -> int:
        from misago.threads.models import Thread
        from misago.users.models import User

        thread = Thread.objects.get(pk=thread_id)
        post = thread.posts.create(
            starter_id=self.bot_user_id, original=content, parsed=content
        )
        return post.pk
