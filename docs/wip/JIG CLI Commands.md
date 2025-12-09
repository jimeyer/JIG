Here's a flat table of all JIG CLI commands:

| Command  | Subcommand | Options/Arguments                                                                                                                                      |
| -------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| jigy     |            | --version, --help                                                                                                                                      |
| impl     |            | --help                                                                                                                                                 |
| impl     | rebuild    | --project-root DIR, --source-dir DIR, --exclude TEXT (multiple), -o/--output PATH, -v/--verbose, --strict/--lenient, --no-timestamp, --skip-validation |
| intent   |            | --help                                                                                                                                                 |
| intent   | rebuild    | --project-root DIR, -o/--output PATH, --no-timestamp                                                                                                   |
| layers   |            | --project-root DIR, --summary, -v/--verbose, --help                                                                                                    |
| layers   | suggest    | --project-root DIR, --apply                                                                                                                            |
| rebuild  |            | --project-root DIR, -v/--verbose                                                                                                                       |
| validate |            | --project-root DIR, --format [human\|json], --help                                                                                                     |
| validate | bricks     | --project-root DIR, --format [human\|json]                                                                                                             |
| validate | full       | --project-root DIR, --format [human\|json]                                                                                                             |
| validate | intent     | --project-root DIR, --format [human\|json]                                                                                                             |
| verify   |            | --help                                                                                                                                                 |
| verify   | rebuild    | --project-root DIR, --test-dir DIR, --no-timestamp                                                                                                     |
|          |            |                                                                                                                                                        |
|          |            |                                                                                                                                                        |

| Command       | Subcommand | Options/Arguments | notes                              |
| ------------- | ---------- | ----------------- | ---------------------------------- |
| jigy          |            |                   |                                    |
| jigy rebuild  |            |                   | does all                           |
| jigy rebuild  | intent     |                   |                                    |
| jigy rebuild  | impl       |                   |                                    |
| jigy rebuild  | verify     |                   |                                    |
| jigy validate |            |                   |                                    |
| jigy validate | intent     |                   |                                    |
| jigy validate | bricks     |                   | show                               |
| jigy update?  |            |                   | do rebuild and validate and bricks |

