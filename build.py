"""Build steps for the Vercel deployment.

Runs after dependencies are installed and before Vercel deploys the app:
applies migrations to the PostgreSQL database from DATABASE_URL, collects
static files, and seeds demo rooms and packages if the catalog is empty
(the seed images are copied from static/images into media/).

Vercel also runs collectstatic automatically; running it here too is harmless.
"""

import os
import subprocess
import sys
import time


def run(*args):
    print(f"+ manage.py {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, "manage.py", *args], check=True)


def run_migrate(retries=3, delay=15):
    """Run migrate, retrying if another deployment is migrating the same
    database at the same time (two pushes close together trigger two
    builds; their post-migrate permission creation can collide with a
    duplicate-key error even though the migrations themselves are fine).
    """
    for attempt in range(1, retries + 1):
        try:
            run("migrate", "--noinput")
            return
        except subprocess.CalledProcessError:
            if attempt == retries:
                raise
            print(
                f"migrate failed (attempt {attempt}/{retries}); retrying "
                f"in {delay}s — another deployment may be migrating the "
                "same database right now.",
                flush=True,
            )
            time.sleep(delay)


def main():
    if not os.environ.get("DATABASE_URL"):
        print(
            "ERROR: DATABASE_URL is not set. Add a PostgreSQL database "
            "(e.g. a free Neon project) and set DATABASE_URL in the "
            "Vercel project environment variables, then redeploy.",
            file=sys.stderr,
        )
        sys.exit(1)

    run_migrate()
    run("collectstatic", "--noinput")
    run("seed_demo", "--if-empty")


if __name__ == "__main__":
    main()
