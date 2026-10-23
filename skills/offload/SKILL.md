---
name: offload
description: Run a CPU-heavy job on the TrueNAS server instead of this machine — copy inputs over with rsync, start the job detached with run-job, watch it with a Monitor, and copy the results back. Use for CPU-bound jobs expected to take over 1 minute locally, or an explicit NAS / TrueNAS request, subject to AGENT.md's local-only restrictions for GPU, display, in-place editing, and credential-bearing inputs.
---

Host, hardware and paths are in AGENT.md "Compute Offload". In the rules below:
`NAS` = `truenas_admin@truenas-scale`, `J` = `/mnt/Raid_1_Storage/jobs`, `<local>` = a folder in this session's scratchpad.

## Preflight

R0. IF this skill starts THEN check AGENT.md Compute Offload O2 and O5 before connecting or transferring inputs.
R0a. IF O2 or O5 applies THEN run the job locally and skip this skill's remote workflow; R0a overrides R1–R15, including lettered sub-rules.
R1. IF R0 permits remote execution THEN run `ssh -o BatchMode=yes NAS 'ls J/bin/run-job J/bin/job-status J/venv/bin/python'`.
R2. IF the SSH login fails THEN stop and report the exact error to the user. Do NOT try other users, hosts, passwords, or API keys.
R3. IF `run-job` or `job-status` is missing on the NAS THEN copy them from this skill's `nas/` folder with `scp` into `J/bin/` and `chmod +x` them.
R4. IF `J/venv/bin/python` is missing THEN stop and tell the user the venv must be rebuilt; describe the rebuild in R7a before doing it.

## Preparing the job

R5. IF a job is started THEN give it the id `<YYYYMMDD>-<short-slug>`, lowercase, letters, digits and hyphens only.
     // Example: `20261018-film-ocr`.
R6. IF the job runs a script THEN the script reads only from `in/`, writes results only to `out/`, and is copied into `in/` with the inputs.
R6a. IF the script writes a result THEN write it to a temporary file in the destination directory, validate its format and expected completeness, and atomically rename it to its final path only after validation succeeds.
     // Commentary: a crash or cancel leaves completed items intact without publishing an interrupted write as a finished result.
R6b. IF the job processes many items THEN the script prints a flushed progress line to stdout at least every 2 minutes, in the form `<done>/<total> ..., ~<N> min left`, and prints `done` as its last line.
R6c. IF the script runs work in parallel THEN use 1 thread per worker AND at most 14 workers AND at most `floor(0.5 × available GB ÷ per-worker GB)` workers, where available GB is the `available` column of `ssh NAS free -g` read just before starting.
     // Commentary: 16 threads total; 2 are left for the NAS's own services. The memory cap binds first for model-based jobs: 14 OCR workers at ~0.75 GB each exhausted the NAS, the kernel killed workers, and the run lost pages.
R6c1. IF the per-worker memory is not known THEN run the script on a small sample first and read one worker's RSS with `ps -o rss`.
     // Example: RapidOCR at 300 dpi ≈ 0.75 GB per worker; with 11 GB available that allows 7 workers.
R6c2. IF the script uses a process pool THEN use `concurrent.futures.ProcessPoolExecutor`, not `multiprocessing.Pool`.
     // Commentary: when a worker is killed, `multiprocessing.Pool` waits forever on its lost task; `ProcessPoolExecutor` raises `BrokenProcessPool` and the job ends with a non-zero status.
R6c3. IF the script resumes an item THEN skip it only when its completion record matches the current input and processing settings AND every recorded output's size and SHA-256 match the final files; existence or non-empty content alone is insufficient.
R6c4. IF an item's final outputs have been published under R6a THEN atomically publish its completion record containing the input and settings fingerprints and each output's size and SHA-256.
R6c5. IF an item's completion record is absent or fails R6c3 THEN recompute that item without reusing its old outputs or temporary files.
R6c6. IF preparing a batch job THEN check its worker script against R6a and R6c3–R6c5 before starting it; adapt a nonconforming script in the job's scratch inputs before launch.
R6d. IF the job is expected to need more than half of the NAS's available memory THEN ask the user before starting it.
R7. IF the job needs a Python package THEN check `J/venv/bin/python -m pip show <pkg>` first, and install only what is missing with `PIP_CACHE_DIR=J/cache J/venv/bin/python -m pip install <pkg>`.
R7a. IF the venv must be rebuilt THEN run `python3 -m venv --without-pip J/venv`, download the pip wheel to `J/cache/pip.whl`, and run `J/venv/bin/python J/cache/pip.whl/pip install --ignore-installed pip`.
     // Commentary: TrueNAS's Python has no ensurepip.
R7b. IF a package installs `opencv-python` THEN uninstall it and install `opencv-python-headless`.
     // Commentary: the NAS has no libGL; the desktop OpenCV build fails to import.
R7c. IF a package needs a system library, root, or Docker THEN stop and ask the user. Do NOT use sudo.
R8. IF the inputs are ready THEN copy them with `rsync -a --mkpath <local>/in/ NAS:J/runs/<id>/in/`.
     // Commentary: without `--mkpath`, rsync cannot create the not-yet-existing `runs/<id>/` folder and the copy fails.

## Running

R9. IF the inputs are copied THEN start the job with `ssh NAS 'J/bin/run-job <id> <command...>'`, where `<command>` runs from `J/runs/<id>/` with the venv first on PATH.
     // Example: `ssh NAS 'J/bin/run-job 20261018-film-ocr python -I in/ocr.py in/frames out/ocr.tsv'`.
R10. IF the job is started THEN watch it with a Monitor (`timeout_ms` 1800000) that every 30 seconds reads `tail -1 log.txt` and `status` over SSH, prints a line only when either changes, and exits when `status` is no longer `running`.
R10a. IF the Monitor expires AND `status` is still `running` THEN re-arm it.
R10b. IF the user asks how long the job will take THEN answer from the latest progress line. IF there is no progress line yet THEN say so.
R11. IF the user asks to cancel a job THEN run `ssh NAS 'kill -- -"$(cat J/runs/<id>/pid)"; echo "exit cancelled" > J/runs/<id>/status'`.
     // Commentary: run-job starts each job with setsid, so `pid` is also the process group id and the negative kill stops the job's children too.

## Collecting

R12. IF `status` reads `exit 0` THEN validate the expected item count, final output formats and completeness, and every batch item's completion record under R6c3 before collecting results.
R12a. IF R12 validation succeeds THEN copy final outputs and completion records with `rsync -a --mkpath NAS:J/runs/<id>/out/ <local>/out/`, excluding temporary files, and verify the copied outputs against the same completeness checks and recorded hashes before reporting success.
R12b. IF remote or copied-result validation fails THEN report the failed checks and stop without reporting success or retrying automatically; R12b overrides R12a.
R13. IF `status` reads `exit <non-zero>` OR `log.txt` contains `Traceback` THEN copy `log.txt` back, show the user its last 20 lines, and stop. Do NOT retry automatically.
R14. IF the results are copied THEN tell the user the run folder `J/runs/<id>/` is kept on the NAS. Delete it only when the user asks.
R15. IF the user asks to clean up old runs THEN list them with `ssh NAS 'J/bin/job-status'` and confirm which ones before deleting.

R16. IF any condition not covered by R0–R15 (including lettered sub-rules) arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.
