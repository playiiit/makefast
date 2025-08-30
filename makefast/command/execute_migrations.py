import importlib.util
import re
import os
import asyncio
from typing import List, Set


class ExecuteMigrations:
    def __init__(self):
        """
        Initialize the migration runner.
        """
        self.migrations_dir = "app/migrations"
        self.executed_file = "venv/Lib/site-packages/makefast/migration/executed_migrations.txt"
        self.executed_migrations: Set[str] = self._load_executed_migrations()

    def _load_executed_migrations(self) -> Set[str]:
        """Load executed migrations from file."""
        if not os.path.exists(self.executed_file):
            return set()

        with open(self.executed_file, 'r') as f:
            return set(line.strip() for line in f if line.strip())

    def _save_executed_migration(self, class_name: str):
        """Save a newly executed migration to file."""
        with open(self.executed_file, 'a') as f:
            f.write(f"{class_name}\n")

    def _get_migration_files(self) -> List[str]:
        """Get all migration files from the directory."""
        files = []
        for file in os.listdir(self.migrations_dir):
            if file.endswith('.py') and file != '__init__.py':
                files.append(file)
        return sorted(files)

    def _parse_import_line(self, line: str) -> tuple[str, str]:
        """
        Parse an import line to get the class name and file name.

        Args:
            line: Import line from __init__.py (e.g., from ._20250205020505_user_two import UserTwo)

        Returns:
            Tuple of (class_name, file_name)
        """
        pattern = r'from \.(\_\d{14}\_[a-zA-Z_]+) import (\w+)'
        match = re.match(pattern, line)
        if not match:
            raise ValueError(f"Invalid import line format: {line}")
        return match.group(2), match.group(1)

    def _import_migration(self, file_name: str, class_name: str):
        """
        Dynamically import a migration class using spec.

        Args:
            file_name: Name of the file without .py extension (e.g., _20250205020505_user_two)
            class_name: Name of the class to import

        Returns:
            Imported class
        """
        file_path = os.path.join(self.migrations_dir, f"{file_name}.py")
        module_name = f"migration_{file_name.replace('.', '_').replace('/', '_')}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec for {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, class_name):
            raise AttributeError(f"Migration class {class_name} not found in {file_path}")

        return getattr(module, class_name)

    async def _execute_migration(self, migration_class) -> None:
        """
        Execute a single migration class.

        Args:
            migration_class: The migration class to execute
        """
        instance = migration_class()
        await instance.run()

    async def run_migrations(self):
        """Execute all migrations in the __init__.py file that haven't been run yet."""
        init_path = os.path.join(self.migrations_dir, '__init__.py')

        if not os.path.exists(init_path):
            raise FileNotFoundError(f"__init__.py not found in {self.migrations_dir}")

        with open(init_path, 'r') as f:
            import_lines = [line.strip() for line in f if line.strip().startswith('from .')]

        # Check if there are any migrations to run
        if not import_lines:
            print("Nothing to migrate")
            return

        # Filter out already executed migrations
        pending_migrations = [
            line for line in import_lines
            if self._parse_import_line(line)[0] not in self.executed_migrations
        ]

        if not pending_migrations:
            print("Nothing to migrate")
            return

        for line in pending_migrations:
            try:
                class_name, file_name = self._parse_import_line(line)

                # Import and run the migration
                migration_class = self._import_migration(file_name, class_name)
                await self._execute_migration(migration_class)

                # Mark as executed and save to file
                self.executed_migrations.add(class_name)
                self._save_executed_migration(class_name)

            except Exception as e:
                print(f"Error executing migration {line}: {str(e)}")
                raise
