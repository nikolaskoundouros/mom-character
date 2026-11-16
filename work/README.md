# work/: saved chat temp folders (16 Nov 2026)

Some scripts still read from two Claude chat temp folders. macOS clears `/private/tmp` on reboot, so copies are kept here.

The scripts still point at the old `/private/tmp` paths. Task 1 in `notes/HANDOFF.md` is to repoint them here and make `./verify.sh` pass.

- `hair-session-e53bbed9/`: from the "Mom's hair recreation plan" chat.
  - `vm/` masks
  - `ana/` analysis
  - `scan/` patch scans
  - `cmp/`, `hi/`, `snaps/`, `bunfr/`, `ref/`
  - `man53/` manual pages
  - `drafts/`
- `fork-session-f3d1b7da/`: from the "FaceTracker Blender video analysis (fork)" chat.
  - `live/`, `mom/`, `momhair/`
  - `hairtut/` tutorial frames
  - `manual/`
  - `podsync/` pod copies, without blender-funnel

`refs/source/` holds the reference clip and its transcript. They are someone else's video, so this repo stays private.
