# syntax = docker/dockerfile:1.2

# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_oim_leaseslicensing

LABEL maintainer="asi@dbca.wa.gov.au"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Australia/Perth \
    EMAIL_HOST="email.server" \
    DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au' \
    NOTIFICATION_EMAIL='none@none.com' \
    NON_PROD_EMAIL='none@none.com' \
    PRODUCTION_EMAIL=False \
    EMAIL_INSTANCE='DEV' \
    SECRET_KEY="ThisisNotRealKey" \
    SITE_PREFIX='lals-dev' \
    SITE_DOMAIN='dbca.wa.gov.au' \
    OSCAR_SHOP_NAME='Parks & Wildlife' \
    BPAY_ALLOWED=False \
    POETRY_VERSION=1.6.1 \
    NODE_MAJOR=20

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list && \
    mv /etc/apt/sourcesau.list /etc/apt/sources.list
# Use Australian Mirrors

RUN --mount=type=cache,target=/var/cache/apt apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
    binutils \
    ca-certificates \
    cron \
    curl \
    gdal-bin \
    gnupg \
    gcc \
    git \
    gunicorn \
    htop \
    libmagic-dev \
    libproj-dev \
    libpq-dev \
    libreoffice \
    libspatialindex-dev \
    mtr \
    patch \
    postgresql-client \
    python3-dev \
    python3-pip \
    python3-setuptools \
    rsyslog \
    sqlite3 \
    ssh \
    sudo \
    tzdata \
    vim \
    wget && \
    rm -rf /var/lib/apt/lists/* && \
    update-ca-certificates

# install node 20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
    | sudo tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip

COPY cron /etc/cron.d/dockercron
COPY startup.sh pre_startup.sh /
COPY ./timezone /etc/timezone
RUN chmod 0644 /etc/cron.d/dockercron && \
    crontab /etc/cron.d/dockercron && \
    touch /var/log/cron.log && \
    service cron start && \
    chmod 755 /startup.sh && \
    chmod +s /startup.sh && \
    chmod 755 /pre_startup.sh && \
    chmod +s /pre_startup.sh && \
    groupadd -g 5000 oim && \
    useradd -g 5000 -u 5000 oim -s /bin/bash -d /app && \
    usermod -a -G sudo oim && \
    echo "oim  ALL=(ALL)  NOPASSWD: /startup.sh" > /etc/sudoers.d/oim && \
    mkdir /app && \
    chown -R oim.oim /app && \
    mkdir /container-config/ && \
    chown -R oim.oim /container-config/ && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    touch /app/rand_hash

FROM builder_base_oim_leaseslicensing as python_dependencies_leaseslicensing
WORKDIR /app
USER oim
ENV PATH=/app/.local/bin:$PATH
COPY --chown=oim:oim gunicorn.ini manage.py manage.sh startup.sh pyproject.toml poetry.lock ./
RUN pip install "poetry==$POETRY_VERSION"
RUN --mount=type=cache,target=~/.cache/pypoetry/cache poetry install --only main --no-interaction --no-ansi

COPY --chown=oim:oim leaseslicensing ./leaseslicensing
COPY --chown=oim:oim .git ./.git

FROM python_dependencies_leaseslicensing as collect_static_leaseslicensing
RUN touch /app/.env && \
    poetry run python manage.py collectstatic --no-input

# The following patches must be applied for seggregated systems when setting up a new environment (i.e. local, dev, uat, prod)
#
# COPY --chown=oim:oim admin.patch.additional
# (local) patch <path of leaseslicensing project>/.venv/lib/<python version>/site-packages/django/contrib/admin/migrations/0001_initial.py admin.patch.additional
# RUN export virtual_env_path=$(poetry env info -p); \
#     export python_version=$(python -c 'import sys; print(str(sys.version_info[0])+"."+str(sys.version_info[1]))'); \
#     patch $virtual_env_path/lib/python$python_version/site-packages/django/contrib/admin/migrations/0001_initial.py admin.patch.additional

# COPY --chown=oim:oim 0001_squashed_0004_auto_20160611_1202.patch
# (local) patch <path of leaseslicensing project>/.venv/lib/<python version>/site-packages/reversion/migrations/0001_initial.py 0001_squashed_0004_auto_20160611_1202.patch
# RUN export virtual_env_path=$(poetry env info -p); \
#     export python_version=$(python -c 'import sys; print(str(sys.version_info[0])+"."+str(sys.version_info[1]))'); \
#     patch $virtual_env_path/lib/python$python_version/site-packages/reversion/migrations/0001_squashed_0004_auto_20160611_1202.py 0001_squashed_0004_auto_20160611_1202.patch
#
# RUN poetry run python manage.py migrate
#
# after running django migrations the patch can be reversed with:
# RUN patch -r $virtual_env_path/lib/python$python_version/site-packages/reversion/migrations/0001_squashed_0004_auto_20160611_1202.py 0001_squashed_0004_auto_20160611_1202.patch


FROM collect_static_leaseslicensing as install_build_vue3_leaseslicensing
RUN cd /app/leaseslicensing/frontend/leaseslicensing ; npm ci --omit=dev && \
    cd /app/leaseslicensing/frontend/leaseslicensing ; npm run build

FROM install_build_vue3_leaseslicensing as launch_leaseslicensing

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/pre_startup.sh"]
