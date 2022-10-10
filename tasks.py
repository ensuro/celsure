from invoke import task, Collection
from py_docker_k8s_tasks import docker_tasks, util_tasks, django_tasks
from py_docker_k8s_tasks.util_tasks import add_tasks

ns = Collection()
add_tasks(ns, docker_tasks)
add_tasks(ns, django_tasks)
add_tasks(ns, util_tasks, "ramdisk")


@ns.add_task
@task
def run(c, port=8000):
    c.run("docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up -d")


@ns.add_task
@task
def restore_db(c, dbname, dump_file):
    kwargs = dict(container="celsure_postgres_1", workdir="/pgdump", user="postgres")
    docker_tasks.docker_exec(
        c, f"dropdb --if-exists {dbname}", **kwargs
    )
    docker_tasks.docker_exec(
        c, f"createdb {dbname}", **kwargs
    )
    docker_tasks.docker_exec(
        c,
        f"pg_restore -x -Fc -d {dbname} {dump_file}",
        **kwargs
    )


@ns.add_task
@task
def refresh_requirements_txt(c, upgrade=False, package=None):
    """Refresh requirements.txt and requirements-dev.txt using pip-tools

    --upgrade will upgrade all packages to latest version
    --package will upgrade a single package
    """
    upgrade = "--upgrade" if upgrade else ""
    package = f"-P {package}" if package is not None else ""
    c.run("cp requirements.in django/")
    c.run("cp requirements.txt django/")
    c.run("cp dev_requirements.in django/")
    c.run("cp dev_requirements.txt django/")
    docker_tasks.docker_exec(c, f"pip-compile {upgrade} {package} requirements.in")
    docker_tasks.docker_exec(c, f"pip-compile {upgrade} {package} dev_requirements.in")
    c.run("rm django/requirements.in")
    c.run("rm django/dev_requirements.in")
    c.run("mv django/requirements.txt .")
    c.run("mv django/dev_requirements.txt .")
