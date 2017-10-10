## Skybeard as executable v??
So, what's changed? Well, a lot.
* The new `beards_as_modules` keyword (also `--beards-as-modules` option)
  imports _any valid module_ as a beard (which means support for staches, old
  style beards, and new style beards with setup.py :tada:)
* `beard_paths` now adds to `sys.path` directly for the lifetime of skybeard
  running
  * As a consequence, using the setting `beards: all` no longer works
  * TODO figure out how to use env variables then we can $(ls -l .) or something
    instead of all
* Skybeard can be run as an executable!
* There is now a default config in `skybeard/default_config.yml` which is
  imported every time skybeard is started.
* Config precidence is as follows: CLI beats config, config beats default
  config.
