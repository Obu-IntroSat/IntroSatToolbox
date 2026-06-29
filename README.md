# IntroSat Toolbox

A modular desktop toolbox for working with embedded devices. Each tool is an
independent app that can be run on its own **or** combined into a single
launcher window with one tab per app.

## Apps

| Package                  | Tab            | What it does                                    |
| ------------------------ | -------------- | ----------------------------------------------- |
| `packages/app_comms`     | Взаимодействие | Talk to a device over a COM (serial) port       |
| `packages/app_firmware`  | Прошивка       | Flash firmware via an external programmer tool  |
| `packages/app_template`  | Шаблон         | Empty starting point for new apps               |
| `shell`                  | —              | Launcher that shows every installed app as a tab|
| `packages/core`          | —              | Shared code (plugin contract, serial, process)  |

## How it fits together

- Every app is a normal Python package that exposes an `AppPlugin`
  (see `packages/core/satcore/plugin.py`).
- Each app registers itself through the `introsat.apps` **entry point** in its
  `pyproject.toml`.
- The launcher (`shell`) discovers all installed apps automatically and builds a
  tab for each. Adding a new app needs **no changes to the launcher**.

```
introsat-toolbox/
├── packages/
│   ├── core/            # shared contract + helpers (satcore)
│   ├── app_comms/       # COM interaction app
│   ├── app_firmware/    # firmware flashing app
│   └── app_template/    # copy this to make a new app
└── shell/               # launcher with tabs
```

## Setup

Use Python 3.10+ and a virtual environment.

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements-dev.txt
```

## Run

Run the combined launcher (all installed apps as tabs):

```bash
introsat
# or: python -m shell.main
```

Run a single app on its own:

```bash
python -m app_comms       # only the COM interaction app
python -m app_firmware    # only the firmware app
python -m app_template    # only the template
```

## Developing just one app

A developer only needs the shared core plus their own app:

```bash
pip install -e packages/core -e packages/app_comms
python -m app_comms
```

## Build executables

Build a single app:

```bash
pyinstaller packages/app_comms/build.spec
# -> dist/app-comms[.exe]
```

Build the combined launcher (bundles every app listed in `shell/build.spec`):

```bash
pyinstaller shell/build.spec
# -> dist/IntroSatToolbox[.exe]
```

> When you add a new app, list its distribution name and package in the
> `APP_DISTRIBUTIONS` / `APP_PACKAGES` lists in `shell/build.spec` so it gets
> bundled into the combined executable.

## Add a new app

1. Copy `packages/app_template` to `packages/app_<name>`.
2. Rename the inner package folder `app_template` -> `app_<name>`.
3. In its `pyproject.toml` update `name`, the `introsat.apps` entry point and the
   `project.scripts` entry.
4. Set `id`, `title`, `order` in `plugin.py` and build your UI in `widget.py`.
5. `pip install -e packages/app_<name>` — it now appears in the launcher.
