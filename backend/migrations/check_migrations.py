import logging
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from collections.abc import Callable
from functools import cached_property
from logging.config import fileConfig
from pathlib import Path
from typing import Any, cast

from alembic import autogenerate
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import Script, ScriptDirectory
from alembic.util import CommandError


class MigrationError(Exception):
    pass


class MultipleHeadsError(MigrationError):
    def __init__(self, heads: list[str]) -> None:
        self.heads = heads
        super().__init__(f"Multiple heads found in Alembic migrations: {heads}.")


class MultipleHeadsInDBError(MigrationError):
    def __init__(self, heads: tuple[str, ...]) -> None:
        self.heads = heads
        super().__init__(f"Multiple heads found in db: {heads}.")


class NoHeadsError(MigrationError):
    def __init__(self) -> None:
        super().__init__("No heads found in Alembic migrations.")


class HasUntrackedSchemaChangesError(MigrationError):
    def __init__(self, changes: list) -> None:
        super().__init__(f"Untracked schema changes found: {changes}.")


class UnknownRevisionError(MigrationError):
    def __init__(self, revision: str) -> None:
        super().__init__(f"Unknown revision: {revision}.")


class AlembicMigrationChecker:
    """
        A class to check for pending Alembic migrations in CI/CD pipelines and before running actual migrations.

        Usage in CI/CD pipelines:
        Because Alembic requires a database connection for most actions,
        and the lack of a database in CI/CD environments, the `--no-db` flag should be used.
        The script will only check for multiple heads in the versions folder.

        $ python -m check_migrations --config path/to/alembic.ini --no-db

        Usage in local development:
        Will fail if there are schema changes.

        $ python -m check_migrations --config path/to/alembic.ini

        Usage before running migrations:
        Because Alembic compares the state of the database with the current state of the models, there will always
        be some schema changes. To avoid the check failing, use the `--silent-diff-check` flag.

        $ python -m check_migrations --config path/to/alembic.ini --silent-diff-check 
        $ alembic upgrade head 
    """

    CONFIG_FILE: Path = Path(__file__).resolve().parents[1] / "alembic.ini"

    def __init__(self) -> None:
        self._args: Any = None

    def setup_arguments(self) -> None:
        parser = ArgumentParser(description=self.__class__.__doc__, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument(
            "--config",
            type=Path,
            default=self.CONFIG_FILE,
            help="Path to the Alembic config file.",
        )
        parser.add_argument(
            "--no-db",
            action="store_true",
            help="Don't check the database for pending migrations.",
            default=False,
        )
        parser.add_argument(
            "--silent-diff-check",
            action="store_true",
            help="Warn but don't fail if there are untracked schema changes.",
            default=False,
        )
        parser.add_argument(
            "-x",
            action="append",
            help="Additional arguments consumed by "
            "custom env.py scripts, e.g. -x "
            "setting1=somesetting -x setting2=somesetting",
        )
        self._args = parser.parse_args()

    def run(self) -> None:
        self.setup_arguments()
        self._logger.info("Starting migration check.")
        self._logger.debug("Using config file: %s", self.CONFIG_FILE)
        try:
            self._run()
        except MigrationError as e:
            self._logger.info("Migration check failed.\n%s", e)
            sys.exit(1)
        except Exception:
            self._logger.exception("An unexpected error occurred.")
            sys.exit(1)
        else:
            self._logger.info("Migration check passed.")
            sys.exit(0)

    def _run(self) -> None:
        head_revision = self._get_head_revision()

        if self._args.no_db:
            return

        db_revision: str | None = self._get_db_revision()

        if not db_revision:
            self._logger.info("No migrations found in the database.")
            return
        if head_revision == db_revision:
            self._logger.info("No pending migrations.")
            return

        pending_migrations: list[str] = [
            f"{step.short_log} ({step.doc})" for step in self._script_directory._upgrade_revs("head", db_revision)
        ]

        self._logger.info("Pending migrations count: %d\n%s", len(pending_migrations), "\n".join(pending_migrations))

    @cached_property
    def _logger(self) -> logging.Logger:
        fileConfig(str(self.CONFIG_FILE))
        return logging.getLogger("alembic.migration_checker")

    @cached_property
    def _config(self) -> Config:
        return Config(file_=str(self.CONFIG_FILE), cmd_opts=self._args)

    @cached_property
    def _script_directory(self) -> ScriptDirectory:
        return ScriptDirectory.from_config(self._config)

    def _get_head_revision(self) -> str:
        self._logger.debug("Getting head revision.")
        heads = self._script_directory.get_heads()
        self._logger.debug("Heads: %s", heads)
        if not heads:
            raise NoHeadsError
        if len(heads) > 1:
            raise MultipleHeadsError(heads)
        return heads[0]

    def _context(
        self, fn: Callable[[tuple[str, ...], MigrationContext], list[Script]], **kwargs: Any
    ) -> EnvironmentContext:
        revision_context = autogenerate.RevisionContext(
            self._config,
            self._script_directory,
            {
                "message": None,
                "autogenerate": True,
                "sql": False,
                "head": "head",
                "splice": False,
                "branch_label": None,
                "version_path": None,
                "rev_id": None,
                "depends_on": None,
                **kwargs,
            },
        )
        return EnvironmentContext(
            self._config,
            self._script_directory,
            fn=fn,
            as_sql=False,
            template_args=revision_context.template_args,
            revision_context=revision_context,
            **kwargs,
        )

    def _get_db_revision(self) -> str | None:
        self._logger.debug("Getting db revision.")
        diff: list[tuple] | None = None
        has_unknown_revision: bool = False
        has_unknown_db_state: bool = False
        last_db_revision: str | tuple[str, ...] | None = None

        def handle_migrations(rev: tuple[str, ...], context: MigrationContext) -> list[Script]:
            self._logger.debug("Handling migration for revision: %s", rev)
            nonlocal diff, last_db_revision, has_unknown_revision, has_unknown_db_state
            if len(rev) > 1:
                has_unknown_db_state = True
                last_db_revision = rev
            elif len(rev) == 1:
                last_db_revision = rev[0]

            self._logger.debug("Comparing metadata.")
            diff = compare_metadata(context, context.opts["target_metadata"])

            if last_db_revision and not has_unknown_db_state:
                self._logger.debug("Getting script for db revision: %s", last_db_revision)
                try:
                    cast("ScriptDirectory", context.script).get_revision(cast("str", last_db_revision))
                except (CommandError, AssertionError):
                    has_unknown_revision = True

            return []

        with self._context(
            fn=handle_migrations,
        ):
            self._script_directory.run_env()

        if diff:
            if self._args.silent_diff_check:
                self._logger.warning("Untracked schema changes found: %s", diff)
            else:
                raise HasUntrackedSchemaChangesError(diff)
        if has_unknown_revision:
            raise UnknownRevisionError(cast("str", last_db_revision))
        if has_unknown_db_state:
            raise MultipleHeadsInDBError(cast("tuple[str, ...]", last_db_revision))
        return cast("str | None", last_db_revision)


def main() -> None:
    checker = AlembicMigrationChecker()
    checker.run()


if __name__ == "__main__":
    main()
