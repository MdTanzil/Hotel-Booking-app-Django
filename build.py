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


def run(*args):
    print(f"+ manage.py {' '.join(args)}", flush=True)
    subprocess.run([sys.executable, "manage.py", *args], check=True)


def main():
    if not os.environ.get("DATABASE_URL"):
        print(
            "ERROR: DATABASE_URL is not set. Add a PostgreSQL database "
            "(e.g. a free Neon project) and set DATABASE_URL in the "
            "Vercel project environment variables, then redeploy.",
            file=sys.stderr,
        )
        sys.exit(1)

    run("migrate", "--noinput")
    run("collectstatic", "--noinput")
    run("seed_demo", "--if-empty")


if __name__ == "__main__":
    main()
